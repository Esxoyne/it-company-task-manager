def theme(request):
    if "is_dark_mode" in request.session:
        is_dark_mode = request.session.get("is_dark_mode")
        return {"is_dark_mode": is_dark_mode}
    return {"is_dark_mode": False}
