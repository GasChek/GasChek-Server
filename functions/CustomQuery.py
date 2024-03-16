from django.core.exceptions import ObjectDoesNotExist
import string
import numpy as np

def get_if_exists(Model, **kwargs):
    try:
        obj = Model.objects.get(**kwargs)
    except ObjectDoesNotExist:
        obj = None
    return obj

def generate_unique_code(Gaschek_Device):
    for _ in range(100):
        chars = string.ascii_lowercase + string.digits
        code = ''.join(np.random.choice(list(chars), size=15))
        exists = get_if_exists(Gaschek_Device, device_id=code)
        if not exists:
            return code
    # device.delete()
    # return False