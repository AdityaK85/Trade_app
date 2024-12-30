# Generated by Django 5.1.2 on 2024-12-21 08:25

import datetime
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdminMaster',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(blank=True, max_length=200, null=True)),
                ('password', models.CharField(blank=True, max_length=200, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CandleData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('exchange', models.CharField(blank=True, max_length=250, null=True)),
                ('token', models.CharField(blank=True, max_length=250, null=True)),
                ('duration', models.IntegerField(blank=True, null=True)),
                ('date', models.DateTimeField()),
                ('open', models.FloatField(blank=True, null=True)),
                ('high', models.FloatField(blank=True, null=True)),
                ('low', models.FloatField(blank=True, null=True)),
                ('close', models.FloatField(blank=True, null=True)),
                ('created_dt', models.DateTimeField(blank=True, default=datetime.datetime(2024, 12, 21, 13, 55, 12, 788714), null=True)),
            ],
        ),
        migrations.CreateModel(
            name='LinkMaster',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('link', models.TextField(blank=True, null=True)),
                ('sequence', models.IntegerField(blank=True, null=True)),
                ('created_date', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='LotSize',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('index_name', models.CharField(blank=True, max_length=250, null=True)),
                ('lot_size', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='MarketFeed',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('market_data', models.CharField(blank=True, default='MASTERTRUST', max_length=300, null=True)),
                ('nifty_open_price', models.FloatField(blank=True, null=True)),
                ('bnf_open_price', models.FloatField(blank=True, null=True)),
                ('nifty_update_time', models.DateField(blank=True, null=True)),
                ('bnf_update_time', models.DateField(blank=True, null=True)),
                ('prev_nifty_closed_price', models.FloatField(blank=True, null=True)),
                ('prev_bnf_closed_price', models.FloatField(blank=True, null=True)),
                ('prev_nifty_changed', models.FloatField(blank=True, null=True)),
                ('prev_bnf_changed', models.FloatField(blank=True, null=True)),
                ('prev_nifty_update_time', models.DateField(blank=True, null=True)),
                ('prev_bnf_update_time', models.DateField(blank=True, null=True)),
                ('created_dt', models.DateTimeField(blank=True, default=datetime.datetime(2024, 12, 21, 13, 55, 12, 788714), null=True)),
            ],
        ),
        migrations.CreateModel(
            name='OptionData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bnf_unique_strikes', models.JSONField(blank=True, null=True)),
                ('bnf_update_unique_dict', models.JSONField(blank=True, null=True)),
                ('bnf_selected_strike', models.JSONField(blank=True, null=True)),
                ('nifty_unique_strikes', models.JSONField(blank=True, null=True)),
                ('nifty_update_unique_dict', models.JSONField(blank=True, null=True)),
                ('nifty_selected_strike', models.JSONField(blank=True, null=True)),
                ('updated_dt', models.DateField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='OptionExpiry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('index', models.CharField(blank=True, max_length=250, null=True)),
                ('expiry', models.DateField(blank=True, null=True)),
                ('created_dt', models.DateTimeField(blank=True, default=datetime.datetime(2024, 12, 21, 13, 55, 12, 787714), null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ResponseLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('response', models.TextField(blank=True, null=True)),
                ('created_date', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='SubscriptionPrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SymbolsMaster',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('trading_symbol', models.CharField(blank=True, max_length=250, null=True)),
                ('symbol', models.CharField(blank=True, max_length=250, null=True)),
                ('expiry', models.IntegerField(blank=True, null=True)),
                ('exchange_code', models.IntegerField(blank=True, null=True)),
                ('exchange', models.CharField(blank=True, max_length=250, null=True)),
                ('token', models.IntegerField(blank=True, null=True)),
                ('company', models.CharField(blank=True, max_length=250, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='TruedataAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(blank=True, max_length=300, null=True)),
                ('password', models.CharField(blank=True, max_length=300, null=True)),
                ('port', models.CharField(blank=True, max_length=300, null=True)),
                ('access_token', models.TextField(blank=True, null=True)),
                ('token_expiry_time', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='MyUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('name', models.CharField(blank=True, max_length=300, null=True)),
                ('email', models.EmailField(blank=True, max_length=300, null=True, unique=True)),
                ('password', models.CharField(blank=True, max_length=200, null=True)),
                ('mobile_no', models.CharField(blank=True, max_length=100, null=True)),
                ('account_status', models.CharField(default='Inactive', max_length=100)),
                ('user_type', models.CharField(blank=True, max_length=100, null=True)),
                ('expired_from', models.DateField(blank=True, null=True)),
                ('created_date', models.DateTimeField(blank=True, null=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('trading_mode', models.CharField(blank=True, default='Live', max_length=300, null=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BreakoutStrategy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('strategy', models.CharField(blank=True, max_length=300, null=True)),
                ('index_type', models.CharField(blank=True, max_length=300, null=True)),
                ('lot_size', models.CharField(blank=True, max_length=300, null=True)),
                ('breakout_candle', models.CharField(blank=True, max_length=300, null=True)),
                ('time_frame', models.CharField(blank=True, max_length=300, null=True)),
                ('breakout_on', models.CharField(blank=True, max_length=300, null=True)),
                ('strike_round_up', models.CharField(blank=True, max_length=300, null=True)),
                ('segment', models.CharField(blank=True, max_length=300, null=True)),
                ('tradingSymbol', models.CharField(blank=True, max_length=300, null=True)),
                ('exchange', models.CharField(blank=True, max_length=300, null=True)),
                ('token', models.CharField(blank=True, max_length=300, null=True)),
                ('open', models.CharField(blank=True, max_length=300, null=True)),
                ('high', models.CharField(blank=True, max_length=300, null=True)),
                ('low', models.CharField(blank=True, max_length=300, null=True)),
                ('close', models.CharField(blank=True, max_length=300, null=True)),
                ('strike_with_round_up_1', models.CharField(blank=True, max_length=300, null=True)),
                ('strike_with_round_up_2', models.CharField(blank=True, max_length=300, null=True)),
                ('strike_round_1', models.CharField(blank=True, max_length=300, null=True)),
                ('strike_round_2', models.CharField(blank=True, max_length=300, null=True)),
                ('option_type', models.CharField(blank=True, max_length=300, null=True)),
                ('subscribe_token', models.CharField(blank=True, max_length=300, null=True)),
                ('expiry_dt', models.DateField(blank=True, null=True)),
                ('is_closed', models.BooleanField(default=False)),
                ('trading_mode', models.CharField(blank=True, max_length=300, null=True)),
                ('create_dt', models.DateTimeField(blank=True, null=True)),
                ('fk_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='BreakoutPosition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_on', models.CharField(blank=True, max_length=300, null=True)),
                ('tradingSymbol', models.CharField(blank=True, max_length=300, null=True)),
                ('high_price', models.CharField(blank=True, max_length=300, null=True)),
                ('low_price', models.CharField(blank=True, max_length=300, null=True)),
                ('strike_round', models.CharField(blank=True, max_length=300, null=True)),
                ('option_type', models.CharField(blank=True, max_length=300, null=True)),
                ('subscribe_token', models.CharField(blank=True, max_length=300, null=True)),
                ('partial_exit', models.CharField(blank=True, max_length=30, null=True)),
                ('partial_target', models.FloatField(blank=True, null=True)),
                ('stop_loss', models.FloatField(blank=True, null=True)),
                ('full_target', models.FloatField(blank=True, null=True)),
                ('max_profit', models.FloatField(blank=True, null=True)),
                ('max_loss', models.FloatField(blank=True, null=True)),
                ('is_tsl_thread', models.BooleanField(default=False)),
                ('tsl', models.FloatField(blank=True, null=True)),
                ('start_tsl_on', models.FloatField(blank=True, null=True)),
                ('pos_status', models.CharField(blank=True, max_length=300, null=True)),
                ('pos_remark', models.CharField(blank=True, max_length=300, null=True)),
                ('thread_flag', models.BooleanField(default=True)),
                ('monitoring_flag', models.BooleanField(default=True)),
                ('market_excuted', models.BooleanField(default=False)),
                ('create_dt', models.DateTimeField(blank=True, null=True)),
                ('fk_strategy', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='algosee_app.breakoutstrategy')),
            ],
        ),
        migrations.CreateModel(
            name='BrokerAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('client_id', models.CharField(blank=True, max_length=50, null=True)),
                ('app_password', models.CharField(blank=True, max_length=50, null=True)),
                ('app_scret', models.CharField(blank=True, max_length=500, null=True)),
                ('app_id', models.CharField(blank=True, max_length=50, null=True)),
                ('app_totp', models.CharField(blank=True, max_length=50, null=True)),
                ('access_token', models.TextField(blank=True, null=True)),
                ('is_login', models.BooleanField(default=False)),
                ('created_dt', models.DateTimeField(blank=True, null=True)),
                ('fk_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ErrorLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('error', models.TextField(blank=True, null=True)),
                ('created_dt', models.DateTimeField(blank=True, default=datetime.datetime(2024, 12, 21, 13, 55, 12, 782714), null=True)),
                ('fk_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Orders',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_mode', models.CharField(blank=True, max_length=10, null=True)),
                ('ltp', models.FloatField(blank=True, null=True)),
                ('qty', models.IntegerField(blank=True, null=True)),
                ('token', models.IntegerField(blank=True, null=True)),
                ('order_id', models.CharField(blank=True, max_length=230, null=True)),
                ('oms_order_id', models.CharField(blank=True, max_length=230, null=True)),
                ('order_side', models.CharField(blank=True, max_length=10, null=True)),
                ('product', models.CharField(blank=True, max_length=10, null=True)),
                ('exchange', models.CharField(blank=True, max_length=10, null=True)),
                ('order_type', models.CharField(blank=True, max_length=10, null=True)),
                ('symbol', models.CharField(blank=True, max_length=30, null=True)),
                ('buyQty', models.IntegerField(blank=True, null=True)),
                ('buyAvg', models.FloatField(blank=True, null=True)),
                ('sellQty', models.IntegerField(blank=True, null=True)),
                ('sellAvg', models.FloatField(blank=True, null=True)),
                ('created_at', models.DateTimeField()),
                ('status', models.CharField(max_length=20)),
                ('entryPrice', models.FloatField(blank=True, null=True)),
                ('exitPrice', models.FloatField(blank=True, null=True)),
                ('exit_at', models.DateTimeField(blank=True, null=True)),
                ('realizedMTM', models.FloatField(blank=True, null=True)),
                ('realizedPNL', models.FloatField(blank=True, null=True)),
                ('remark', models.TextField(blank=True, null=True)),
                ('is_exit', models.BooleanField(default=False)),
                ('is_square_off', models.BooleanField(default=False)),
                ('is_square_off_thread', models.BooleanField(default=False)),
                ('currentQty', models.IntegerField(blank=True, null=True)),
                ('fk_strategy', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='algosee_app.breakoutposition')),
            ],
        ),
        migrations.CreateModel(
            name='TargetSl_Monitor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('target', models.FloatField(blank=True, null=True)),
                ('sl', models.FloatField(blank=True, null=True)),
                ('remark', models.TextField(blank=True, null=True)),
                ('live_target', models.FloatField(blank=True, null=True)),
                ('live_sl', models.FloatField(blank=True, null=True)),
                ('live_remark', models.TextField(blank=True, null=True)),
                ('nfty_target_points', models.FloatField(blank=True, null=True)),
                ('bnf_target_points', models.FloatField(blank=True, null=True)),
                ('equity_target_points', models.FloatField(blank=True, null=True)),
                ('create_dt', models.DateTimeField(blank=True, null=True)),
                ('fk_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TradingMode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mode', models.BooleanField()),
                ('fk_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
