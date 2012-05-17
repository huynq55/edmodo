__author__ = 'KIEN'
from django import template

register = template.Library()

@register.filter
def notification_number(notification, user):
    participated_thread_set=user.participated_thread_set.all()
    if participated_thread_set.count()>0:
        for participated_thread in participated_thread_set:
            posts=participated_thread.thread.post_set.filter(created__gt=participated_thread.last_modify)
            notification+=posts.count()
    return notification