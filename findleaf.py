from extras.scripts import Script, ObjectVar
from dcim.models import Device, Interface
from dcim.choices import InterfaceStatusChoices

class LeafSpineValidator(Script):
    class Meta:
        name = "Weryfikacja połączeń Leaf-Spine"
        description = "Weryfikuje poprawność okablowania między Leaf a Spine"

    # Krok 1: Wybór urządzenia Leaf
    leaf_device = ObjectVar(
        model=Device,
        label="Leaf Switch",
        query_params={'role': 'leaf-switch'},
        description="Wybierz urządzenie z rolą Leaf"
    )

    # Krok 2: Wybór portu na Leaf
    leaf_interface = ObjectVar(
        model=Interface,
        label="Port docelowy",
        depends_on=['leaf_device'],
        query_params={'device_id': '$leaf_device'},
        description="Wybierz port do weryfikacji"
    )

    def run(self, data, commit):
        device = data['leaf_device']
        interface = data['leaf_interface']
        
        self.log_info(f"Rozpoczęto weryfikację dla {device} port {interface}")

        # Weryfikacja roli urządzenia
        if not device.device_role.slug == 'leaf-switch':
            self.log_failure("Wybrane urządzenie nie ma roli Leaf!")
            return

        # Sprawdzenie połączenia kablowego
        if not interface.cable:
            self.log_failure("Brak przypisanego kabla do portu!")
            return
            
        # Znajdź drugi koniec kabla
        spine_interface = None
        for termination in interface.cable.terminations.all():
            if termination.interface != interface:
                spine_interface = termination.interface
                break

        if not spine_interface:
            self.log_failure("Brak zakończenia kabla po stronie Spine!")
            return

        spine_device = spine_interface.device

        # Weryfikacja roli Spine
        if not spine_device.device_role.slug == 'spine-switch':
            self.log_failure(f"Podłączone urządzenie {spine_device} nie jest Spine!")
            return

        # Weryfikacja konfiguracji portu Spine
        validation_passed = True
        error_messages = []
        
        # Sprawdź custom field 'leaf_connection'
        expected_value = f"{device.name}:{interface.name}"
        actual_value = spine_interface.custom_fields.get('leaf_connection')
        
        if actual_value != expected_value:
            validation_passed = False
            error_messages.append(
                f"Nieprawidłowa wartość custom field: "
                f"Oczekiwano '{expected_value}', Jest '{actual_value}'"
            )

        # Sprawdź status portu
        if spine_interface.status != InterfaceStatusChoices.STATUS_ACTIVE:
            validation_passed = False
            error_messages.append("Port Spine jest wyłączony!")

        # Generowanie raportu
        if validation_passed:
            self.log_success("Weryfikacja zakończona pomyślnie!")
            self.log_info(f"Podłączony Spine: {spine_device} port {spine_interface}")
        else:
            self.log_failure("Znaleziono błędy:")
            for msg in error_messages:
                self.log_failure(msg)

        return "Kompletna weryfikacja zakończona"
