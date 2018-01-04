class statusbar(models.Model):
    _name = 'statusbar.demo'
    name = fields.Char('Name', required=True)
    """
    This selection field contains all the possible values for the statusbar.
    The first part is the database value, the second is the string that is showed. Example:
    ('finished','Done'). 'finished' is the database key and 'Done' the value shown to the user
    """
    state = fields.Selection([
            ('concept', 'Concept'),
            ('started', 'Started'),
            ('progress', 'In progress'),
            ('finished', 'Done'),
            ],default='concept')

    <record model="ir.ui.view" id="view_statusbar_form">
    <field name="name">Statusbar</field>
    <field name="model">statusbar.demo</field>
    <field name="type">form</field>
    <field name="arch" type="xml">
    <form string="Workflow record">
    <!--The header tag is built to add buttons within. This puts them at the top -->
    <header>
        <button string="Set to concept" type="object" name="concept_progressbar" attrs="{'invisible': [('state', '=', 'concept')]}"/>
        <!--The oe_highlight class gives the button a red color when it is saved.
        It is usually used to indicate the expected behaviour. -->
        <button string="Set to started" type="object" name="started_progressbar" class="oe_highlight" attrs="{'invisible': [('state','!=','concept')]}"/>
        <button string="In progress" type="object" name="progress_progressbar" attrs="{'invisible': [('state','=','progress')]}"/>
        <button string="Done" type="object" name="done_progressbar" attrs="{'invisible': [('state','=','finished')]}"/>
        <!--This will create the statusbar, thanks to the widget. -->
        <field name="state" widget="statusbar"/>
    </header>
    <group>
        <field name="name"/>
    </group>
        </form>
    </field>
</record>




    @api.multi
    def create_invoice_two(self):
        solicitud = self.browse()
        ir_model_data = self.env['ir.model.data']
        form_res = ir_model_data.get_object_reference(cr, uid, 'account', 'invoice_form')
        form_id = form_res and form_res[1] or False
        property_obj = self.env['ir.property']
        #get account_id for invoice
        rec_pro_id = property_obj.search([('name','=','property_account_receivable')])
        rec_line_data = property_obj.read(['name','value_reference'])
        account_id =  rec_line_data [0]['value_reference'].split(',')[1]
        # get sale account_id for invoice_line
        sale_pro_id = property_obj.search([('name','=','property_account_income_categ')])
        sale_line_data = property_obj.read(,['name','value_reference'])
        sale_account_id =  sale_line_data [0]['value_reference'].split(',')[1]
        #get partner_id for invoice
        name_id = int(self.name)
        
        #get data for invoice
        context['type'] = 'out_invoice'
        context['active_id'] = name_id
        invoice_pool = self.env['account.invoice']
        default_fields = invoice_pool.fields_get(cr, uid, context=context)
        invoice_default = invoice_pool.default_get(cr, uid, default_fields, context=context)
        onchange_partner = invoice_pool.onchange_partner_id(cr, uid, [], type='out_invoice', partner_id=name_id)
        invoice_default.update(onchange_partner['value'])
        lines = []
        # get the invoice lines
        for prod in solicitud.product_fee:
            line_data = {
                'uos_id': False, 
                'product_id': False,
                'price_unit': prod.product_fee.list_price, 
                'account_id': sale_account_id, 
                'name': prod.product_fee.name,
                'discount': 0, 
                'account_analytic_id': prod.account_analytic_id.id, 
                'invoice_line_tax_id': [[6, False, []]], 
                'quantity': 1
                }
            invoice_line= [0,False,line_data]
            lines.append(invoice_line)

        
        invoice_data = {
                        'partner_id': name_id,
                        'date_invoice': self.date_invoice,
                        'account_id': account_id,#determine the account for invoice 'account receivable'
                        'invoice_line': lines,
                        }
      
        invoice_default.update(invoice_data)
        invoice_id = invoice_pool.create(cr, uid, invoice_default, context=context)
        



        ##################################################################################################
##################################################################################################
##################################################################################################
##################################################################################################
##################################################################################################
##################################################################################################
##################################################################################################
##################################################################################################
    # @api.multi
    # def create_invoice_two2(self):
    #     solicitud = self.browse()

    #     #get account_id for invoice
    #     account_id = self.invoice_receivable_account_id.id
    #     # get sale account_id for invoice_line
        
    #     #get partner_id for invoice
    #     name_id = int(self.name)
        
    #     #get data for invoice

    #     invoice_pool = self.env['account.invoice']
    #     #default_fields = invoice_pool.fields_get(cr, uid, context=context)
    #     #invoice_default = invoice_pool.default_get(cr, uid, default_fields, context=context)
    #     invoice_default = invoice_pool
    #     #onchange_partner = invoice_pool.onchange_partner_id(cr, uid, [], type='out_invoice', partner_id=name_id)
    #     onchange_partner = invoice_pool.onchange_partner_id(type='out_invoice', partner_id=name_id)
    #     invoice_default.update(onchange_partner['value'])
    #     # get the invoice lines
    #     product_coop_id = self.product_fee.id
    #     product_coop = self.env['product.coop'].search([('id','=',product_coop_id)])
    #     company = self.company_id
    #     lista = []
    #     for reg in product_coop.product:
    #         name = _('%s.\n''Cuota de ingreso nvo socio ') % (product_coop.product.name)
    #         amount = product_coop.product.list_price
    #         line_data = self.env['account.invoice.line'].with_context(force_company=company.id).product_id_change(product_coop.product.id, product_coop.product.uom_id.id, qty=1.0, name='', type='out_invoice', partner_id=partner.id, fposition_id=partner.property_account_position.id, company_id=company.id)
    #         account_id = int(product_coop.product.property_account_income)
    #         line_vals = {'product_id': product_coop.product.id, 
    #             'name': name, 
    #             'price_unit': amount,
    #             'quantity': 1.0,
    #             'account_id': account_id, 
    #             'invoice_line_tax_id': [(6, 0, line_data['value'].get('invoice_line_tax_id', []))],
    #             }
    #         invoice_linea = [(0,False,line_vals)]
    #         lista.append(line_vals)
    #     return lista

        
    #     invoice_data = {
    #                     'partner_id': name_id,
    #                     'date_invoice': self.date_invoice,
    #                     'account_id': account_id,#determine the account for invoice 'account receivable'
    #                     'invoice_line': lista,
    #                     }
      
    #     invoice_default.update(invoice_data)
    #     invoice_id = invoice_pool.create( invoice_default)
    #     