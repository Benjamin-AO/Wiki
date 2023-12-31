import random
import markdownify
from markdown2 import Markdown
from django import forms
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render
from . import util



class NewPageForm(forms.Form):
    newPage_title = forms.CharField(widget= forms.TextInput(attrs={'placeholder':'New Entry Title', 'maxlength':50}), label=False)
    newPageContent_Html = forms.CharField(widget= forms.Textarea(attrs={'class':'textarea', 'placeholder':'Enter the contents for this new page here', 'rows':50, 'cols':40, }), label=False)


def convert_md_to_html(title):
    content = util.get_entry(title)
    markdowner = Markdown()
    if content == None:
        return None
    else:
        return markdowner.convert(content)


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
    })


def entry(request, title):
    html_content = convert_md_to_html(title)
    if html_content == None:
        return render(request, "encyclopedia/errorPage.html", {
            "error_code": "404 Error",
            "error_message": "The requested page doesn't exist!"
        })
    else:
        return render(request, "encyclopedia/entry.html", {
            "entryTitle": title,
            "entryResource": html_content
        })


def search(request):
    entry_list = util.list_entries()
    if request.method == "POST":
        search_query = request.POST['q']
        html_content = convert_md_to_html(search_query)
        if html_content is not None:
            for existing_entry in entry_list:
                if search_query.lower() in existing_entry.lower():
                    return render(request, "encyclopedia/entry.html", {
                        "entryTitle": existing_entry,
                        "entryResource": html_content   
                    })
        else:
            querySubString = []
            for existing_entry in entry_list:
                if search_query.lower() in existing_entry.lower():
                    querySubString.append(existing_entry)

            if len(querySubString) > 0:
                return render(request, "encyclopedia/search.html", {
                    "search_query": search_query,
                    "similarResource": querySubString,
            })

            else:
                return render(request, "encyclopedia/emptySearch.html", {
                "search_response": search_query.title()
            })


def add_newPage(request):
    ''' this function will create a new wiki page based on request received from newPage.html'''
    if request.method == "POST":
        form = NewPageForm(request.POST)
        if form.is_valid():
            newPage_title = form.cleaned_data["newPage_title"]
            newPageContent_Html = form.cleaned_data["newPageContent_Html"]
            #newPageContent_Html_with_heading = f"<h1>{newPage_title}</h1> \n{newPageContent_Html}" # will add title header to mark down.
            newPageContent_md = markdownify.markdownify(newPageContent_Html, heading_style="ATX")
            
            all_entries = util.list_entries()
            all_entries_upper = []
            for existing_title in all_entries: 
                all_entries_upper.append(existing_title.upper())

            new_page_title_upper = newPage_title.upper()

            if  new_page_title_upper not in all_entries_upper:
                page_maker = util.save_entry(newPage_title, newPageContent_md)
                return entry(request, newPage_title)     
            else:
                return render(request,"encyclopedia/alreadyExists.html", {
                    "error_code": "403 Error",
                    "newPage_title": newPage_title
                })
    return render(request, "encyclopedia/newPage.html", {
        "form": NewPageForm(),
    })


def edit_page(request):
    if request.method == "POST":
        page_title = request.POST["entryTitle"]
        page_content = util.get_entry(page_title)
        return render(request, "encyclopedia/editPage.html",{
            "entryTitle": page_title,
            "entryContent": page_content,
        })


def save_edit(request):
    if request.method == "POST":
        title = request.POST["entryTitle"]
        content = request.POST["entryContent"]
        util.save_entry(title, content)
        return entry(request, title)
        

def cancel_edit(request):
    if request.method == "POST":
        title = request.POST["entryTitle"]
        return entry(request, title)


def random_page(request):
    title_collections = []
    title_list = util.list_entries()
    for title in title_list:
        title_collections.append(title)
    random_title = random.choice(title_collections)
    return entry(request, random_title)