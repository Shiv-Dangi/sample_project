# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import multiselectfield.db.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Admin_User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('loginid', models.CharField(max_length=50)),
                ('password', models.CharField(max_length=80)),
                ('email', models.CharField(max_length=50)),
                ('roles', models.CharField(max_length=50)),
                ('mobile', models.CharField(max_length=50)),
                ('gender', models.CharField(max_length=50)),
                ('company', models.CharField(max_length=50)),
                ('address', models.TextField()),
                ('dateofbirth', models.CharField(max_length=50)),
                ('is_attendance_enable', models.BooleanField()),
                ('is_login_enable', models.BooleanField()),
                ('is_active', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='AllOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_number', models.CharField(max_length=50)),
                ('order_status', models.CharField(max_length=50)),
                ('onlinepay_status', models.CharField(max_length=50, null=True)),
                ('offer_from_web', models.CharField(max_length=50, null=True)),
                ('branch_assigned_at', models.DateTimeField(null=True)),
                ('branch_assigned', models.CharField(max_length=50)),
                ('placed_at', models.DateTimeField(null=True)),
                ('expected_at', models.DateTimeField(null=True)),
                ('no_of_people', models.CharField(max_length=15, null=True)),
                ('accepted_by', models.CharField(max_length=50)),
                ('accepted_at', models.DateTimeField(null=True)),
                ('dispatched_by', models.CharField(max_length=50)),
                ('dispatched_at', models.DateTimeField(null=True)),
                ('dispatched_with', models.CharField(max_length=50)),
                ('delivered_at', models.DateTimeField(null=True)),
                ('paid_at', models.DateTimeField(null=True)),
                ('payment_mode', models.CharField(max_length=50)),
                ('delivery_type', models.CharField(max_length=50)),
                ('customer_name', models.CharField(max_length=50)),
                ('customer_mobile', models.CharField(max_length=50)),
                ('source', models.CharField(max_length=50)),
                ('address', models.TextField(null=True)),
                ('special_comment', models.CharField(max_length=100)),
                ('ordered_items', models.CharField(max_length=3500)),
                ('subtotal', models.CharField(max_length=50)),
                ('coupon_applied', models.CharField(max_length=50)),
                ('discount_percent', models.CharField(max_length=50)),
                ('vat_percent', models.CharField(max_length=50)),
                ('service_charge_percent', models.CharField(max_length=50)),
                ('service_tax_percent', models.CharField(max_length=50)),
                ('e_wallet', models.CharField(default=0, max_length=50)),
                ('delivery_charge', models.CharField(default=0, max_length=20)),
                ('grand_total', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Branch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('branch', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='CollectiontoDelboy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField()),
                ('amount', models.FloatField()),
                ('collected_at', models.DateTimeField(null=True)),
                ('delivery_boy', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='app.Admin_User')),
            ],
        ),
        migrations.CreateModel(
            name='CounterOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_number', models.CharField(max_length=50)),
                ('ordered_at', models.DateTimeField()),
                ('order_status', models.CharField(default=b'active', max_length=50)),
                ('assigned_at', models.DateTimeField(null=True)),
                ('bill_print', models.DateTimeField(null=True)),
                ('ordered_items', models.CharField(max_length=3500)),
                ('subtotal', models.CharField(max_length=50)),
                ('discount_percent', models.CharField(max_length=50)),
                ('vat_percent', models.CharField(max_length=50)),
                ('service_charge_percent', models.CharField(max_length=50)),
                ('service_tax_percent', models.CharField(max_length=50)),
                ('grand_total', models.FloatField()),
                ('assigned_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='app.Admin_User')),
            ],
        ),
        migrations.CreateModel(
            name='CounterOrdernumber',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='CounterTable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('table_number', models.IntegerField()),
                ('table_name', models.CharField(max_length=50)),
                ('max_occupy', models.IntegerField()),
                ('is_active', models.BooleanField(default=True)),
                ('order_number', models.CharField(default=b'', max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='CouponInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('coupon_number', models.CharField(max_length=40)),
                ('order_number', models.CharField(max_length=50, null=True)),
                ('prefix', models.CharField(max_length=10)),
                ('suffix', models.CharField(max_length=10)),
                ('start_from', models.IntegerField()),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('discount_type', models.CharField(max_length=10)),
                ('discount_amount', models.IntegerField()),
                ('blocked', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Coupons',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num_of_coupons', models.IntegerField()),
                ('prefix', models.CharField(max_length=10)),
                ('suffix', models.CharField(max_length=10)),
                ('start_from', models.IntegerField()),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('discount_type', models.CharField(max_length=10)),
                ('discount_value', models.IntegerField()),
                ('is_active', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_name', models.CharField(max_length=40)),
                ('customer_number', models.CharField(max_length=40)),
                ('customer_address', models.TextField(null=True)),
                ('isblocked', models.BooleanField(default=False)),
                ('order_number', models.CharField(max_length=40)),
            ],
        ),
        migrations.CreateModel(
            name='DeliveryCharge',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('delivery_charge', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Expense',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField()),
                ('expense_for', models.CharField(max_length=80)),
                ('amount', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='ExpenseCollection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField()),
                ('collection_for', models.CharField(max_length=80)),
                ('amount', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='ForOrdernumber',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='InventoryDependency',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='InventoryItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_name', models.CharField(max_length=50, unique=True)),
                ('quantity', models.FloatField()),
                ('alert_quantity', models.FloatField()),
                ('alert_number', models.CharField(max_length=10)),
                ('alert_email', models.EmailField(max_length=30)),
            ],
            options={
                'verbose_name': 'Inventory Item',
                'verbose_name_plural': 'Inventory Items',
            },
        ),
        migrations.CreateModel(
            name='InventoryPurchase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField()),
                ('quantity', models.FloatField()),
                ('bill_no', models.CharField(max_length=50, null=True)),
                ('amount', models.FloatField(null=True)),
                ('item_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.InventoryItem')),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_name', models.CharField(max_length=50)),
                ('item_subname', models.CharField(max_length=50)),
                ('item_code', models.CharField(max_length=50)),
                ('price', models.CharField(max_length=50)),
                ('serves', models.CharField(default=0, max_length=50)),
                ('del_time', models.CharField(default=b'Immediate', max_length=50)),
                ('advance_pay', models.CharField(default=b'N.A.', max_length=50)),
                ('discount', models.CharField(max_length=50)),
                ('item_description', models.CharField(max_length=400)),
                ('item_type', models.CharField(max_length=50)),
                ('is_active', models.BooleanField()),
                ('active_on_website', models.BooleanField(default=True)),
                ('active_on_app', models.BooleanField(default=True)),
                ('active_on_callcenter', models.BooleanField(default=True)),
                ('active_on_counter', models.BooleanField(default=True)),
                ('active_on_outside', models.BooleanField(default=True)),
                ('image', models.CharField(default=b'http://delivery.lhdindia.com/Files/Image/LHD_NA.jpg', max_length=250)),
            ],
        ),
        migrations.CreateModel(
            name='Item_Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_category', models.CharField(max_length=50)),
                ('is_home_display', models.BooleanField()),
                ('is_active', models.BooleanField()),
                ('image', models.CharField(default=b'http://delivery.lhdindia.com/Files/Image/LHD_NA.jpg', max_length=250)),
            ],
        ),
        migrations.CreateModel(
            name='Item_Subcategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subcategory_name', models.CharField(max_length=100)),
                ('belongs_to_category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Item_Category')),
            ],
        ),
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('membership_id', models.IntegerField(primary_key=True, serialize=False)),
                ('membership_name', models.CharField(max_length=50, unique=True)),
                ('discount', models.DecimalField(decimal_places=2, max_digits=4)),
                ('is_active', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='Offer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('offer_name', models.CharField(max_length=100)),
                ('offer_image', models.CharField(max_length=200)),
                ('applicable_on', models.CharField(max_length=50)),
                ('offer_date', models.DateField()),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('description', models.CharField(max_length=800)),
                ('discount', models.CharField(default=20, max_length=10)),
                ('delivery_days', multiselectfield.db.fields.MultiSelectField(choices=[(1, b'Sunday'), (2, b'Monday'), (3, b'Tuesday'), (4, b'Wednesday'), (5, b'Thursday'), (6, b'Friday'), (7, b'Saturday')], max_length=13)),
                ('payment_mode', multiselectfield.db.fields.MultiSelectField(choices=[(b'cod', b'Cash on Delivery'), (b'online', b'Online Payment'), (b'smd', b'Sodexo Meal Passes'), (b'credit', b'Credit')], max_length=21)),
                ('is_active', models.BooleanField(default=False)),
                ('is_default_membership_applied', models.BooleanField(default=False)),
                ('are_coupon_applied', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='OfferMenu',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('daytime', models.CharField(max_length=50, null=True)),
                ('discount_percent', models.CharField(max_length=20)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Item')),
                ('offer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Offer')),
            ],
        ),
        migrations.CreateModel(
            name='OrderSource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Partner',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('loginid', models.CharField(max_length=20, unique=True)),
                ('password', models.CharField(max_length=50)),
                ('email', models.CharField(max_length=50)),
                ('mobile', models.CharField(max_length=10)),
                ('address', models.TextField()),
                ('partner_name', models.CharField(max_length=100)),
                ('owner_number', models.CharField(max_length=10)),
                ('contact_number', models.CharField(max_length=10)),
                ('service_tax_number', models.CharField(max_length=50)),
                ('vat_number', models.CharField(max_length=50)),
                ('logo_link', models.URLField()),
                ('vat_percent', models.DecimalField(decimal_places=2, max_digits=5)),
                ('service_charge_percent', models.DecimalField(decimal_places=2, max_digits=5)),
                ('service_tax_percent', models.DecimalField(decimal_places=2, max_digits=5)),
                ('e_wallet', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('my_counter', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('credit_limit', models.IntegerField(default=0)),
                ('otp_required', models.BooleanField(default=False)),
                ('city', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.City')),
                ('membership_type', models.ForeignKey(default=3, on_delete=django.db.models.deletion.CASCADE, to='app.Membership')),
            ],
        ),
        migrations.CreateModel(
            name='PartnerMenu',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('expected_price', models.CharField(max_length=20)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Item')),
                ('partner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Partner')),
            ],
        ),
        migrations.CreateModel(
            name='PayDeliveryBoy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField()),
                ('amount', models.FloatField()),
                ('delivery_boy', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='app.Admin_User')),
            ],
        ),
        migrations.CreateModel(
            name='PaymentMode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_mode', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='PromotionImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image_url', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='PromotionVideo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('video', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='RestrictedAreas',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('restricted_areas', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=100)),
                ('phone', models.CharField(max_length=10, unique=True)),
                ('password', models.CharField(max_length=80)),
                ('email', models.CharField(max_length=50)),
                ('gender', models.CharField(max_length=20)),
                ('address', models.TextField(null=True)),
                ('company', models.CharField(default=b'Lazeez Hakeem', max_length=50)),
                ('block_user', models.BooleanField(default=False)),
                ('credit_limit', models.DecimalField(decimal_places=2, default=0.0, max_digits=9)),
                ('otp', models.IntegerField(default=0)),
                ('e_wallet', models.DecimalField(decimal_places=2, default=0.0, max_digits=8)),
                ('date_of_birth', models.DateField(null=True)),
                ('branch', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='app.Branch')),
                ('city', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='app.City')),
                ('membership_type', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='app.Membership')),
            ],
        ),
        migrations.CreateModel(
            name='Waiter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('userid', models.CharField(max_length=50)),
                ('password', models.CharField(max_length=50)),
            ],
        ),
        migrations.AddField(
            model_name='item',
            name='item_category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Item_Category'),
        ),
        migrations.AddField(
            model_name='item',
            name='item_subcategory',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Item_Subcategory'),
        ),
        migrations.AddField(
            model_name='inventorydependency',
            name='dependency_name',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Item'),
        ),
        migrations.AddField(
            model_name='inventorydependency',
            name='inventory_item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.InventoryItem'),
        ),
        migrations.AddField(
            model_name='counterorder',
            name='assigned_waiter',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='app.Waiter'),
        ),
        migrations.AddField(
            model_name='counterorder',
            name='branch',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='app.Branch'),
        ),
        migrations.AddField(
            model_name='counterorder',
            name='customer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='app.Customer'),
        ),
        migrations.AddField(
            model_name='counterorder',
            name='payment_mode',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='app.PaymentMode'),
        ),
        migrations.AddField(
            model_name='counterorder',
            name='table_no',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.CounterTable'),
        ),
        migrations.AddField(
            model_name='admin_user',
            name='branch',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Branch'),
        ),
        migrations.AddField(
            model_name='admin_user',
            name='city',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.City'),
        ),
    ]
