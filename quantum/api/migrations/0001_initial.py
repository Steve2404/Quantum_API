# Generated by Django 5.1.1 on 2024-09-26 04:36

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Kme',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('key_size', models.IntegerField(default=256)),
                ('stored_key_count', models.IntegerField(default=0)),
                ('max_key_count', models.IntegerField(default=10000)),
                ('max_key_per_request', models.IntegerField(default=1)),
                ('max_key_size', models.IntegerField(default=256)),
                ('min_key_size', models.IntegerField(default=128)),
                ('max_SAE_ID_count', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='UninitKey',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('key_uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('key', models.BinaryField()),
                ('other_kme_id', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Sae',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(default='user', max_length=255, null=True)),
                ('sae_certificate_serial', models.BinaryField(blank=True, null=True)),
                ('kme', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.kme')),
                ('master_sae', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.sae')),
            ],
        ),
        migrations.CreateModel(
            name='Key',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key_uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('key_data', models.BinaryField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('origin_sae', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='origin_keys', to='api.sae')),
                ('target_sae', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='target_keys', to='api.sae')),
            ],
        ),
    ]
