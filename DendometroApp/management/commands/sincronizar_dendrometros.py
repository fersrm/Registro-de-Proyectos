from django.core.management.base import BaseCommand, CommandError
from DendometroApp.models import Dendrometro
from DendometroApp.services import sync
from DendometroApp.services.thingspeak import ThingSpeakError


class Command(BaseCommand):
    help = 'Descarga lecturas aunque nadie tenga abierta la web. Ejecutar periódicamente con cron/tarea programada.'

    def add_arguments(self, parser):
        parser.add_argument('--sensor', type=int)
        parser.add_argument('--completo', action='store_true', help='Reconsultar toda la ventana configurada.')
        parser.add_argument('--max-pasos', type=int, default=400)

    def handle(self, *args, **options):
        sensors = Dendrometro.objects.filter(activo=True)
        if options['sensor']:
            sensors = sensors.filter(pk=options['sensor'])
            if not sensors.exists():
                raise CommandError('No existe ese dendrómetro activo.')
        for sensor in sensors:
            try:
                job = sync.start(sensor, force=options['completo'])
                if job:
                    for _ in range(max(1, options['max_pasos'])):
                        if job.estado != 'pendiente':
                            break
                        if job.lease_until and job.lease_until > sync.timezone.now():
                            break
                        job = sync.step(job)
                    self.stdout.write(f'{sensor.nombre}: {job.estado}; {job.registros} registros procesados.')
                    if job.error:
                        self.stderr.write(job.error)
            except ThingSpeakError as exc:
                self.stderr.write(f'{sensor.nombre}: {exc}')
