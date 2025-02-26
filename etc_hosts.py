class GetEtcHosts(Script):
    class Meta:
        name = "Generuj /etc/hosts"
        description = (
            ""
        )
        scheduling_enabled = False

    def run(self, data, commit):
        output = ""
        for s in Site.objects.all():
            output += f"####### {s.name} #######\n"
            for dr in DeviceRole.objects.all():
                output += f"### {dr.name} ###\n"
                for dev in Device.objects.filter(site=s, role=dr):
                    primary_ip4_address = (
                        None  # Inicjalizacja zmiennej dla adresu primary_ip4
                    )

                    transformed_dev_name = re.sub(
                        r"[\s\(\)\[\]\{\},;:\'\"?!\-]+", "-", dev.name
                    )
                    transformed_dev_name = transformed_dev_name.strip("-")

                    # Sprawdzenie i zapisanie adresu primary_ip4
                    if dev.primary_ip4:
                        primary_ip4_address = dev.primary_ip4.address.ip
                        output += f"{primary_ip4_address} {transformed_dev_name} {transformed_dev_name.lower()}\n"

                    # Dodawanie linii dla każdego interfejsu, pomijając primary_ip4, jeśli się zgadza
                    for interface in dev.interfaces.all():
                        if interface.ip_addresses:
                            for ip_address in interface.ip_addresses.all():
                                # Pominięcie, jeśli adres IP interfejsu jest adresem primary_ip4
                                if ip_address.address.ip == primary_ip4_address:
                                    continue
                                transformed_interface_name = (
                                    f"{transformed_dev_name}-{interface.name}"
                                )
                                output += f"{ip_address.address.ip} {transformed_interface_name}\n"

        return output