from django.core.management.base import BaseCommand, CommandError
from django.db import connections
from django.db.migrations.executor import MigrationExecutor


class Command(BaseCommand):
    help = 'Check DB connectivity and unapplied migrations (exit non-zero on problems)'

    def handle(self, *args, **options):
        # Check DB connectivity
        try:
            conn = connections['default']
            c = conn.cursor()
            c.execute('SELECT 1')
            c.fetchone()
        except Exception as e:
            raise CommandError(f'Database connectivity problem: {e}')

        # Check for unapplied migrations
        try:
            executor = MigrationExecutor(connections['default'])
            targets = executor.loader.graph.leaf_nodes()
            plan = executor.migration_plan(targets)
            if plan:
                raise CommandError('There are unapplied migrations')
        except CommandError:
            raise
        except Exception as e:
            raise CommandError(f'Error checking migrations: {e}')

        self.stdout.write(self.style.SUCCESS('OK'))
