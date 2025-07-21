from django.contrib.auth.models import User

from .models import Profile, Link

from threading import Thread
import os
import time
import schedule
import traceback

# Job scheduling

def jobs():
    """
    background job scheduler that runs scheduled tasks in threads
    """
    schedule.every(1).minutes.do(check_profiles)
    schedule.every(1).minutes.do(delete_expired_links)

    while True:
        try:
            schedule.run_pending()
        except Exception as e:
            print(f"\n/!\\ Error in job scheduler: {e}:\n{traceback.format_exc()}")
        finally:
            time.sleep(1)


def start_job_scheduler():
    """
    start the job scheduler in a daemon thread when the django app starts
    """
    if os.environ.get("RUN_MAIN") != "true":
        return  # prevent starting the scheduler multiple times in development
        
    job_thread = Thread(target=jobs)
    job_thread.daemon = True  # avoid blocking shutdown
    job_thread.start()


# Job workers

def check_profiles(user:User=None):
    """
    make sure that each user has a profile
    """
    if user is not None:
        affected_users = [user]
    else:
        affected_users = [affected for affected in User.objects.all()]
    
    for affected in affected_users:
        try:
            profile = affected.profile
        except Profile.DoesNotExist:
            profile = Profile(user=affected)
            profile.save()


def delete_expired_links(user:User=None):
    """
    depending on the user preferences, deletes expired links
    """
    if user is not None:
        if not user.profile.delete_expired:
            return  # don't delete anything if the user doesn't want to
        affected_users = [user]
    else:
        affected_users = [affected for affected in User.objects.all() if affected.profile.delete_expired]
    
    for affected in affected_users:
        links = [link for link in affected.link_set.all() if not link.active()]
        for link in links:
            link.delete()
