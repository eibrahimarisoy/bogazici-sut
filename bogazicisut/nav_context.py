from order.models import Category, Order

def nav_data(request):
    context = dict()
    context['categories'] = Category.objects.all()
    order = Order.objects.filter(session_key=request.session.session_key, status="waiting").last()
    if order is None:
        context['item_count'] = 0
    else:
        context['item_count'] = order.items.count()
    return context


