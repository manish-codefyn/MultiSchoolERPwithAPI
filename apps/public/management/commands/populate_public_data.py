from django.core.management.base import BaseCommand
from apps.public.models import FeatureModule, PricingPlan, PricingFeature

class Command(BaseCommand):
    help = 'Populates public website with initial data (Features, Pricing)'

    def handle(self, *args, **kwargs):
        self.populate_features()
        self.populate_pricing()
        self.stdout.write(self.style.SUCCESS('Successfully populated public data'))

    def populate_features(self):
        self.stdout.write('Populating Features...')
        
        # Clear existing
        # FeatureModule.objects.all().delete()
        
        features_data = [
            {
                'title': 'Academic Planning',
                'description': 'Curriculum design, course management, and academic calendar with automated scheduling.',
                'icon': 'bi-journal-check',
                'color_class': 'primary',
                'display_order': 1
            },
            {
                'title': 'Attendance System',
                'description': 'Automated attendance tracking with biometric integration and real-time notifications.',
                'icon': 'bi-clipboard-check',
                'color_class': 'primary',
                'display_order': 2
            },
            {
                'title': 'Examination & Grading',
                'description': 'Comprehensive exam management with automated grading and performance analytics.',
                'icon': 'bi-graph-up',
                'color_class': 'primary',
                'display_order': 3
            },
            {
                'title': 'User Management',
                'description': 'Role-based access control for students, teachers, staff, and administrators.',
                'icon': 'bi-people',
                'color_class': 'success',
                'display_order': 4
            },
            {
                'title': 'Fee Management',
                'description': 'Automated fee collection, receipt generation, and financial reporting system.',
                'icon': 'bi-wallet',
                'color_class': 'success',
                'display_order': 5
            },
            {
                'title': 'Event Management',
                'description': 'Plan and manage institutional events, holidays, and academic activities.',
                'icon': 'bi-calendar-event',
                'color_class': 'success',
                'display_order': 6
            },
             {
                'title': 'Notification System',
                'description': 'Multi-channel notifications via SMS, email, and push notifications.',
                'icon': 'bi-bell',
                'color_class': 'warning',
                'display_order': 7
            },
            {
                'title': 'Messaging Platform',
                'description': 'Real-time messaging between students, teachers, and parents.',
                'icon': 'bi-chat-square-text',
                'color_class': 'warning',
                'display_order': 8
            },
            {
                'title': 'Financial Reports',
                'description': 'Comprehensive financial reporting and analytics with visual dashboards.',
                'icon': 'bi-graph-up-arrow',
                'color_class': 'danger',
                'display_order': 9
            },
        ]

        for data in features_data:
            FeatureModule.objects.update_or_create(
                title=data['title'],
                defaults=data
            )

    def populate_pricing(self):
        self.stdout.write('Populating Pricing...')
        
        # Clear existing plans to ensure fresh start with new structure
        PricingPlan.objects.all().delete()
        
        # Plan 1: Starter (Up to 200)
        starter, _ = PricingPlan.objects.update_or_create(
            slug='starter',
            defaults={
                'name': 'Starter',
                'price': 4599,
                'currency': 'INR',
                'interval': 'yearly',
                'description': 'Perfect for small schools & coaching centers',
                'is_popular': False,
                'button_text': 'Start Free Trial',
                'display_order': 1
            }
        )
        self.create_features(starter, [
            ('Up to 200 Students', True),
            ('Core Academic Module', True),
            ('Attendance Tracking', True),
            ('Basic Fee Management', True),
            ('Email Support', True),
            ('Mobile App Access', False),
        ])

        # Plan 2: Growth (Up to 500)
        growth, _ = PricingPlan.objects.update_or_create(
            slug='growth',
            defaults={
                'name': 'Growth',
                'price': 9999,
                'currency': 'INR',
                'interval': 'yearly',
                'description': 'For growing institutions needing more power',
                'is_popular': True,
                'highlight_text': 'Best Value',
                'button_text': 'Get Started',
                'display_order': 2
            }
        )
        self.create_features(growth, [
            ('Up to 500 Students', True),
            ('All Starter Features', True),
            ('Examination & Grading', True),
            ('Parent Mobile App', True),
            ('SMS Integration', True),
            ('Priority Support', True),
        ])

        # Plan 3: Standard (Up to 1000)
        standard, _ = PricingPlan.objects.update_or_create(
            slug='standard',
            defaults={
                'name': 'Standard',
                'price': 14599,
                'currency': 'INR',
                'interval': 'yearly',
                'description': 'Advanced features for established schools',
                'is_popular': False,
                'button_text': 'Get Started',
                'display_order': 3
            }
        )
        self.create_features(standard, [
            ('Up to 1000 Students', True),
            ('All Growth Features', True),
            ('Library Management', True),
            ('Transport Management', True),
            ('Inventory System', True),
            ('Dedicated Account Manager', True),
        ])

        # Plan 4: Enterprise (Unlimited)
        enterprise, _ = PricingPlan.objects.update_or_create(
            slug='enterprise',
            defaults={
                'name': 'Enterprise',
                'price': 0,  # 0 indicates "Contact Sales"
                'currency': 'INR',
                'interval': 'yearly',
                'description': 'Full-scale solution for large campuses',
                'is_popular': False,
                'button_text': 'Contact Sales',
                'display_order': 4
            }
        )
        self.create_features(enterprise, [
            ('Unlimited Students', True),
            ('All Standard Features', True),
            ('Custom Domain & Branding', True),
            ('Dedicated Server Option', True),
            ('API Access & Webhooks', True),
            ('Custom Development', True),
            ('24/7 Dedicated Support', True),
        ])

    def create_features(self, plan, features_list):
        # Clear existing features for idempotency
        plan.features.all().delete()
        for idx, (text, included) in enumerate(features_list):
            PricingFeature.objects.create(
                plan=plan,
                text=text,
                is_included=included,
                display_order=idx
            )
