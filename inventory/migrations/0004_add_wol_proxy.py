# inventory/migrations/0004_add_wol_proxy.py
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('inventory', '0003_alter_software_uninstall'),
    ]
    
    operations = [
        migrations.AddField(
            model_name='entity',
            name='wol_proxy',
            field=models.ForeignKey(
                'inventory.machine',
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='wol_proxy_for_entities',
                verbose_name='Proxy WOL',
                help_text='Machine du site qui enverra les WOL localement'
            ),
        ),
        migrations.AddField(
            model_name='machine',
            name='is_wol_proxy',
            field=models.BooleanField(
                default=False,
                verbose_name='Est un proxy WOL'
            ),
        ),
    ]
