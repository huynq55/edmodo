__author__ = 'KIEN'
from django import template
from django.utils.safestring import mark_safe

register = template.Library()
@register.filter
def search_highlight(searched_string, query_word_set):
    searched_string_word_set=searched_string.split()
    for i in range(0,len(searched_string_word_set)):
        lower_searched_string_word=searched_string_word_set[i].lower()
        for query_word in query_word_set:
            index=lower_searched_string_word.find(query_word.lower())
            if index != -1:
                if index==0:
                    searched_string_word_set[i]="<span class=\"searched_word\">"+ searched_string_word_set[i][index:index+len(query_word)]+"</span>"+ searched_string_word_set[i][index+len(query_word):]
                else:
                    searched_string_word_set[i]=searched_string_word_set[i][:index]+"<span class=\"searched_word\">"+ searched_string_word_set[i][index:index+len(query_word)]+"</span>"+ searched_string_word_set[i][index+len(query_word):]
                break
    result=' '.join(searched_string_word_set)
    return mark_safe(result)
