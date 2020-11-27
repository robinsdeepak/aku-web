from django.shortcuts import render


def home(request):
    context = {"title": "Home"}
    return render(request, 'base/homepage.html', context)


def result_links_view(request):
    result_links_data = [
        (batch, {i: "#" for i in range(1, 7)})
        for batch in ["2016-2020", "2017-2021", "2018-2022", "2019-2023", ]
    ]
    context = {
        "title": "Results",
        "result_links_data": result_links_data,
    }
    return render(request, 'web/result_links.html', context)
