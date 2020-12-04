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


def registration_no(request, batch, semester):
    context = {
        'batch': batch,
        'semester': semester,
    }

    if request.method == 'GET':
        return render(request, 'web/input_registration_no.html', context=context)

    elif request.method == 'POST':
        reg_no = request.POST['reg']
        year = batch[2:4]
        file = f"results/{year}sem{semester}/{reg_no}.html"
        return render(request, file, context=context)


def ranks(request):
    rank_links_data = [
        (batch, ['CIVIL', 'CSE', 'EEE', 'MECH'])
        for batch in ["2016-2020", "2017-2021", "2018-2022", "2019-2023"]
    ]
    context = {
        "title": "Rank",
        "rank_links_data": rank_links_data,
        "rank_link_page": True
    }
    return render(request, 'web/rank_links.html', context)


def rank_page(request, batch, branch):
    context = {
        "batch": batch,
        "branch": branch,
        "data_path": "ranks/data/126-2016-110.csv"
    }
    return render(request, 'web/data_table.html', context=context)
