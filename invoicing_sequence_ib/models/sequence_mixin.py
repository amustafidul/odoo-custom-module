from odoo import models, fields, api, _
from datetime import datetime

class SequenceMixin(models.AbstractModel):
    _inherit = 'sequence.mixin'

    def _set_next_sequence(self):
        """Set the next sequence.

        This method ensures that the field is set both in the ORM and in the database.
        This is necessary because we use a database query to get the previous sequence,
        and we need that query to always be executed on the latest data.

        :param field_name: the field that contains the sequence.
        """
        self.ensure_one()
        last_sequence = self._get_last_sequence()
        new = not last_sequence
        if new:
            last_sequence = self._get_last_sequence(relaxed=True) or self._get_starting_sequence()

        format, format_values = self._get_sequence_format_param(last_sequence)
        sequence_number_reset = self._deduce_sequence_number_reset(last_sequence)
        if new:
            date_start, date_end = self._get_sequence_date_range(sequence_number_reset)
            format_values['seq'] = 0
            format_values['year'] = self._truncate_year_to_length(date_start.year, format_values['year_length'])
            format_values['year_end'] = self._truncate_year_to_length(date_end.year, format_values['year_end_length'])
            format_values['month'] = date_start.month
        format_values['seq'] = format_values['seq'] + 1
        if self.move_type == 'out_invoice':
            seq_name = format.format(**format_values)
            seq_name = seq_name.split('/')

            if str(datetime.today().year) in seq_name:
                if self.env.user.code_branch:
                    seq_name[seq_name.index(str(datetime.today().year))] = '%s/' % (self.env.user.code_branch) + str(datetime.today().year)[-2:] + '/%s' % (str(datetime.now().month).zfill(2))
                else:
                    seq_name[seq_name.index(str(datetime.today().year))] = str(
                        datetime.today().year)[-2:] + '/%s' % (str(datetime.now().month).zfill(2))
                seq_name = '/'.join(seq_name)

            formatted_string = format.format(**format_values)
            modified_string = formatted_string.replace(formatted_string, seq_name)

            self[self._sequence_field] = modified_string
            self._compute_split_sequence()
        elif self.move_type == 'in_invoice':
            seq_name = format.format(**format_values)
            seq_name = seq_name.split('/')
            seq_name[0] = 'BILLS'

            if str(datetime.today().year) in seq_name:
                if self.env.user.code_branch:
                    seq_name[seq_name.index(str(datetime.today().year))] = '%s/' % (self.env.user.code_branch) + str(datetime.today().year)[-2:]
                else:
                    seq_name[seq_name.index(str(datetime.today().year))] = str(
                        datetime.today().year)[-2:]
                seq_name = '/'.join(seq_name)

            formatted_string = format.format(**format_values)
            modified_string = formatted_string.replace(formatted_string, seq_name)



            self[self._sequence_field] = modified_string
            self._compute_split_sequence()