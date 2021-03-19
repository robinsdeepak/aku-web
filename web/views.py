from django.shortcuts import render


def home(request):
    context = {"title": "Home"}
    return render(request, 'base/homepage.html', context)


def result_links_view(request):
    result_links_data = [
        ('2016-2020', {1: '#', 2: '#', 3: '#', 4: '#', 5: '#', 6: '#', 7: '#', 8: '#'}),
        ('2017-2021', {1: '#', 2: '#', 3: '#', 4: '#', 5: '#', 6: '#'}),
        ('2018-2022', {1: '#', 2: '#', 3: '#', 4: '#'}),
        ('2019-2023', {1: '#', 2: '#'})
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


branch_code_map = {
    "CIVIL": 101,
    "MECH": 102,
    "EEE": 110,
    "CSE": 105
}


def rank_page(request, batch, branch):
    version = 1.0
    context = {
        "batch": batch,
        "branch": branch,
        "version": version,
        "data_path": f"ranks/data/126-{batch[:4]}-{branch_code_map[branch]}.csv"
    }
    return render(request, 'web/data_table.html', context=context)
