# from __future__ import absolute_import
# from management.commands.delete_inactive_models import Command
# from datetime import timedelta
# from celery import shared_task
# from accounts.models import User, Gas_Dealer


# @shared_task()
# def delete_inactive_models():
#     inactive_models = User.objects.filter(is_verified=False)
#     for model in inactive_models:
#         dealer = Gas_Dealer.objects.filter(user=model).first()

#         if dealer:
#             dealer.delete()
#         model.delete()

# delete_inactive_models.delay()
