from . import res_config_settings
from . import customer
from . import document
from . import invoice
from . import payment_method
from . import product
from . import room
from . import store
from . import supplier
from . import sync
from . import table

# Check for bugs
if not res_config_settings:
    raise ValueError("res_config_settings is null")
if not customer:
    raise ValueError("customer is null")
if not document:
    raise ValueError("document is null")
if not invoice:
    raise ValueError("invoice is null")
if not payment_method:
    raise ValueError("payment_method is null")
if not product:
    raise ValueError("product is null")
if not room:
    raise ValueError("room is null")
if not store:
    raise ValueError("store is null")
if not supplier:
    raise ValueError("supplier is null")
if not sync:
    raise ValueError("sync is null")
if not table:
    raise ValueError("table is null")
