from odoo.addons.l10n_sa_edi.wizard.account_move_reversal import AccountMoveReversal
from odoo.exceptions import UserError

# Patch the method
def custom_reverse_moves(self, is_modify=False):
    # Simply bypass the original Saudi check
    return super(AccountMoveReversal, self).reverse_moves(is_modify=is_modify)

AccountMoveReversal.reverse_moves = custom_reverse_moves
