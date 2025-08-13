from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
import random

from accounts.models import User, UserProfile
from locations.models import ZipArea, DeliveryZone
from stores.models import Store, StoreZipCoverage
from catalog.models import Category, Product, StoreProduct, Ingredient
from core.models import Address

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample data for the multi-store ecommerce platform'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating sample data...'))
        
        # Create ZIP areas
        self.create_zip_areas()
        
        # Create users
        self.create_users()
        
        # Create categories
        self.create_categories()
        
        # Create products
        self.create_products()
        
        # Create ingredients
        self.create_ingredients()
        
        # Create stores
        self.create_stores()
        
        # Create store products
        self.create_store_products()
        
        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))

    def create_zip_areas(self):
        """Create sample ZIP areas."""
        zip_areas_data = [
            {'zip_code': '110001', 'area_name': 'Connaught Place', 'city': 'New Delhi', 'state': 'Delhi'},
            {'zip_code': '110002', 'area_name': 'Darya Ganj', 'city': 'New Delhi', 'state': 'Delhi'},
            {'zip_code': '110003', 'area_name': 'Kashmere Gate', 'city': 'New Delhi', 'state': 'Delhi'},
            {'zip_code': '400001', 'area_name': 'Fort', 'city': 'Mumbai', 'state': 'Maharashtra'},
            {'zip_code': '400002', 'area_name': 'Kalbadevi', 'city': 'Mumbai', 'state': 'Maharashtra'},
            {'zip_code': '560001', 'area_name': 'Chickpet', 'city': 'Bangalore', 'state': 'Karnataka'},
            {'zip_code': '560002', 'area_name': 'Chikkamahalakshmi', 'city': 'Bangalore', 'state': 'Karnataka'},
        ]
        
        for data in zip_areas_data:
            zip_area, created = ZipArea.objects.get_or_create(
                zip_code=data['zip_code'],
                defaults={
                    'area_name': data['area_name'],
                    'city': data['city'],
                    'state': data['state'],
                    'is_serviceable': True,
                }
            )
            if created:
                self.stdout.write(f'Created ZIP area: {zip_area}')

    def create_users(self):
        """Create sample users."""
        # Create admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@freshmeat.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write('Created admin user (username: admin, password: admin123)')
        
        # Create customer users
        customers_data = [
            {'username': 'john_doe', 'email': 'john@example.com', 'first_name': 'John', 'last_name': 'Doe'},
            {'username': 'jane_smith', 'email': 'jane@example.com', 'first_name': 'Jane', 'last_name': 'Smith'},
        ]
        
        for data in customers_data:
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'email': data['email'],
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'role': 'customer',
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                self.stdout.write(f'Created customer user: {user.username}')
        
        # Create store owners
        store_owners_data = [
            {'username': 'store_owner1', 'email': 'owner1@example.com', 'first_name': 'Raj', 'last_name': 'Kumar'},
            {'username': 'store_owner2', 'email': 'owner2@example.com', 'first_name': 'Priya', 'last_name': 'Sharma'},
            {'username': 'store_owner3', 'email': 'owner3@example.com', 'first_name': 'Ahmed', 'last_name': 'Khan'},
        ]
        
        for data in store_owners_data:
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'email': data['email'],
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'role': 'store_owner',
                }
            )
            if created:
                user.set_password('owner123')
                user.save()
                self.stdout.write(f'Created store owner: {user.username}')

    def create_categories(self):
        """Create sample categories."""
        categories_data = [
            {'name': 'Chicken', 'icon': 'fas fa-drumstick-bite'},
            {'name': 'Mutton', 'icon': 'fas fa-bacon'},
            {'name': 'Fish', 'icon': 'fas fa-fish'},
            {'name': 'Prawns', 'icon': 'fas fa-shrimp'},
            {'name': 'Marinated', 'icon': 'fas fa-pepper-hot'},
        ]
        
        for i, data in enumerate(categories_data):
            category, created = Category.objects.get_or_create(
                name=data['name'],
                defaults={
                    'icon': data['icon'],
                    'display_order': i,
                    'is_active': True,
                }
            )
            if created:
                self.stdout.write(f'Created category: {category}')

    def create_products(self):
        """Create sample products."""
        categories = Category.objects.all()
        
        products_data = {
            'Chicken': [
                {'name': 'Chicken Breast (Boneless)', 'sku': 'CHK001', 'weight_grams': 500},
                {'name': 'Chicken Legs (With Bone)', 'sku': 'CHK002', 'weight_grams': 1000},
                {'name': 'Chicken Wings', 'sku': 'CHK003', 'weight_grams': 500},
                {'name': 'Whole Chicken', 'sku': 'CHK004', 'weight_grams': 1500},
            ],
            'Mutton': [
                {'name': 'Mutton Curry Cut', 'sku': 'MUT001', 'weight_grams': 500},
                {'name': 'Mutton Biryani Cut', 'sku': 'MUT002', 'weight_grams': 1000},
                {'name': 'Mutton Keema', 'sku': 'MUT003', 'weight_grams': 500},
                {'name': 'Lamb Chops', 'sku': 'MUT004', 'weight_grams': 500},
            ],
            'Fish': [
                {'name': 'Pomfret (Medium)', 'sku': 'FSH001', 'weight_grams': 500},
                {'name': 'Salmon Fillet', 'sku': 'FSH002', 'weight_grams': 250},
                {'name': 'Kingfish Steaks', 'sku': 'FSH003', 'weight_grams': 500},
                {'name': 'Tuna Steaks', 'sku': 'FSH004', 'weight_grams': 300},
            ],
            'Prawns': [
                {'name': 'Tiger Prawns (Large)', 'sku': 'PRW001', 'weight_grams': 500},
                {'name': 'Medium Prawns', 'sku': 'PRW002', 'weight_grams': 500},
                {'name': 'Jumbo Prawns', 'sku': 'PRW003', 'weight_grams': 250},
            ],
            'Marinated': [
                {'name': 'Tandoori Chicken', 'sku': 'MAR001', 'weight_grams': 500},
                {'name': 'Chicken Tikka', 'sku': 'MAR002', 'weight_grams': 500},
                {'name': 'Seekh Kebab', 'sku': 'MAR003', 'weight_grams': 500},
            ]
        }
        
        for category in categories:
            if category.name in products_data:
                for product_data in products_data[category.name]:
                    product, created = Product.objects.get_or_create(
                        sku=product_data['sku'],
                        defaults={
                            'name': product_data['name'],
                            'category': category,
                            'description': f'Fresh {product_data["name"].lower()} sourced from trusted suppliers.',
                            'weight_grams': product_data['weight_grams'],
                            'is_active': True,
                        }
                    )
                    if created:
                        self.stdout.write(f'Created product: {product}')

    def create_ingredients(self):
        """Create sample ingredients."""
        ingredients_data = [
            {'name': 'Extra Spice', 'price': 10.00},
            {'name': 'Less Salt', 'price': 0.00},
            {'name': 'Ginger Garlic Paste', 'price': 15.00},
            {'name': 'Mint Leaves', 'price': 5.00},
            {'name': 'Lemon Juice', 'price': 5.00},
        ]
        
        for data in ingredients_data:
            ingredient, created = Ingredient.objects.get_or_create(
                name=data['name'],
                defaults={
                    'price': Decimal(str(data['price'])),
                    'is_active': True,
                }
            )
            if created:
                self.stdout.write(f'Created ingredient: {ingredient}')

    def create_stores(self):
        """Create sample stores."""
        owners = User.objects.filter(role='store_owner')
        zip_areas = ZipArea.objects.all()
        
        stores_data = [
            {
                'name': 'Fresh Meat Corner',
                'store_code': 'FMC001',
                'description': 'Your neighborhood fresh meat store with premium quality products.',
                'phone_number': '+91-9876543210',
                'email': 'contact@freshmeatcorner.com',
                'min_order_amount': 200,
                'delivery_fee': 50,
                'opens_at': '08:00',
                'closes_at': '22:00',
            },
            {
                'name': 'Ocean Fresh Seafood',
                'store_code': 'OFS001',
                'description': 'Premium seafood and fish delivered fresh daily.',
                'phone_number': '+91-9876543211',
                'email': 'orders@oceanfresh.com',
                'min_order_amount': 300,
                'delivery_fee': 75,
                'opens_at': '09:00',
                'closes_at': '21:00',
            },
            {
                'name': 'Meat Palace',
                'store_code': 'MPL001',
                'description': 'Royal taste of premium meat and poultry.',
                'phone_number': '+91-9876543212',
                'email': 'info@meatpalace.com',
                'min_order_amount': 250,
                'delivery_fee': 60,
                'opens_at': '07:00',
                'closes_at': '23:00',
            },
        ]
        
        for i, store_data in enumerate(stores_data):
            owner = owners[i % len(owners)]
            
            # Create address for store
            address = Address.objects.create(
                line1=f"Store Address {i+1}",
                city=zip_areas[i % len(zip_areas)].city,
                state=zip_areas[i % len(zip_areas)].state,
                zip_code=zip_areas[i % len(zip_areas)].zip_code,
            )
            
            store, created = Store.objects.get_or_create(
                store_code=store_data['store_code'],
                defaults={
                    'name': store_data['name'],
                    'description': store_data['description'],
                    'owner': owner,
                    'address': address,
                    'phone_number': store_data['phone_number'],
                    'email': store_data['email'],
                    'min_order_amount': Decimal(str(store_data['min_order_amount'])),
                    'delivery_fee': Decimal(str(store_data['delivery_fee'])),
                    'opens_at': store_data['opens_at'],
                    'closes_at': store_data['closes_at'],
                    'status': 'active',
                    'is_active': True,
                }
            )
            
            if created:
                self.stdout.write(f'Created store: {store}')
                
                # Create store ZIP coverage
                coverage_zips = zip_areas[i:i+3] if i+3 <= len(zip_areas) else zip_areas[i:]
                for zip_area in coverage_zips:
                    coverage, created = StoreZipCoverage.objects.get_or_create(
                        store=store,
                        zip_area=zip_area,
                        defaults={
                            'estimated_delivery_time_minutes': random.randint(30, 60),
                            'is_active': True,
                        }
                    )
                    if created:
                        self.stdout.write(f'  - Added coverage for {zip_area.zip_code}')

    def create_store_products(self):
        """Create store-specific products with pricing."""
        stores = Store.objects.all()
        products = Product.objects.all()
        
        for store in stores:
            # Each store gets 60-80% of all products
            store_products_count = int(len(products) * random.uniform(0.6, 0.8))
            selected_products = random.sample(list(products), store_products_count)
            
            for product in selected_products:
                base_price = random.uniform(200, 800)  # Base price range
                compare_price = base_price * random.uniform(1.1, 1.3)  # 10-30% markup for compare price
                
                store_product, created = StoreProduct.objects.get_or_create(
                    store=store,
                    product=product,
                    defaults={
                        'price': Decimal(f'{base_price:.2f}'),
                        'compare_at_price': Decimal(f'{compare_price:.2f}'),
                        'stock_quantity': random.randint(5, 50),
                        'low_stock_threshold': 5,
                        'is_available': True,
                        'is_featured': random.choice([True, False]),
                    }
                )
                
                if created:
                    self.stdout.write(f'  - Added {product.name} to {store.name} at ₹{base_price:.2f}')