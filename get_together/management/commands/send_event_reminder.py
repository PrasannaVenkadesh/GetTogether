import datetime
import time
import urllib

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from django.template.loader import get_template, render_to_string
from django.urls import reverse
from django.utils import timezone

from accounts.models import EmailRecord
from events.models import Attendee, Event


class Command(BaseCommand):
    help = "Sends upcomming event notifications to attendees."

    def handle(self, *args, **options):
        site = Site.objects.get(id=1)

        # Events that start within a day.
        query = Q(
            status=Attendee.YES,
            event__start_time__gt=timezone.now(),
            event__start_time__lt=timezone.now() + datetime.timedelta(days=1),
        )

        attendees = Attendee.objects.filter(query)

        for attendee in attendees:

            # Skip people who don't want notificiations or have no email address.
            if not attendee.user.send_notifications or not attendee.user.user.email:
                continue

            # Skip people who have been reminded in the last day.
            if (
                attendee.last_reminded
                and timezone.now() - datetime.timedelta(days=1) < attendee.last_reminded
            ):
                continue

            context = {"event": attendee.event}

            email_subject = "Upcoming event reminder"
            email_body_text = render_to_string(
                "get_together/emails/events/reminder.txt", context
            )
            email_body_html = render_to_string(
                "get_together/emails/events/reminder.html", context
            )
            email_recipients = [attendee.user.user.email]
            email_from = getattr(
                settings, "DEFAULT_FROM_EMAIL", "noreply@gettogether.community"
            )

            success = send_mail(
                from_email=email_from,
                html_message=email_body_html,
                message=email_body_text,
                recipient_list=email_recipients,
                subject=email_subject,
            )

            attendee.last_reminded = timezone.now()
            attendee.save()

            EmailRecord.objects.create(
                sender=None,
                recipient=attendee.user.user,
                email=attendee.user.user.email,
                subject=email_subject,
                body=email_body_text,
                ok=success,
            )
            time.sleep(0.1)
