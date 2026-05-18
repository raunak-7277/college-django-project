# Generated manually for role-based staff user reporting.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('call', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='email',
            field=models.EmailField(blank=True, default='', max_length=254),
        ),
    ]
