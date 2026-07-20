from django.db import migrations


def seed_networks(apps, schema_editor):
    Network = apps.get_model("networks", "Network")
    networks = [
        ("Airtel", "TELECOM"),
        ("Vodacom", "TELECOM"),
        ("Yas/Tigo", "TELECOM"),
        ("Halotel", "TELECOM"),
        ("CRDB", "BANK"),
        ("NMB", "BANK"),
        ("NBC", "BANK"),
    ]
    Network.objects.bulk_create(
        [Network(name=name, network_type=ntype) for name, ntype in networks]
    )


def reverse_seed(apps, schema_editor):
    Network = apps.get_model("networks", "Network")
    Network.objects.filter(
        name__in=["Airtel", "Vodacom", "Yas/Tigo", "Halotel", "CRDB", "NMB", "NBC"]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("networks", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_networks, reverse_seed),
    ]
