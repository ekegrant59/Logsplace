from core.models import Wallet, Category

def default(request):
    
    if request.user.is_authenticated:
        check_wallet = Wallet.objects.filter(user=request.user).count()
        if check_wallet:
            pass
        else:
            create_wallet = Wallet.objects.create(
                user=request.user,
                email=request.user.email,
                balance=0,
            )
    else:
        pass
    
    all_cat = Category.objects.all()
    
    try:
        balance = Wallet.objects.get(user=request.user)
        balance = balance.balance
    except:
        balance = 0

    return {
        "balance": balance,
        "base_all_cat": all_cat,
    }