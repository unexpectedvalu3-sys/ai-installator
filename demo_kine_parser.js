const data = $input.first().json;
const values = data.values || [];
if (values.length < 2) return [{ json: { _skip: true } }];

const headers = values[0];
const rows = values.slice(1);
const tomorrow = new Date(Date.now() + 86400000).toISOString().slice(0, 10);

const results = [];
for (let i = 0; i < rows.length; i++) {
  const row = Object.fromEntries(headers.map((h, j) => [h, rows[i][j] || '']));
  // Nettoyage numéro de téléphone : retire apostrophe Sheets, normalise en +33
  let tel = (row.telephone || '').replace(/^['']/, '').trim();
  if (!tel.startsWith('+')) {
    if (tel.startsWith('0') && tel.length === 10) tel = '+33' + tel.slice(1);
    else if (tel.startsWith('33')) tel = '+' + tel;
  }
  row.telephone = tel;
  if (row.date_rdv === tomorrow && row.rappel_envoye === '') {
    const subject = 'Rappel RDV demain - Cabinet ' + row.praticien;
    const body = 'Bonjour ' + row.prenom + ',\n\nNous vous rappelons votre rendez-vous de kinesitherapie prevu demain le ' + row.date_rdv + ' a ' + row.heure + ' au cabinet de ' + row.praticien + '.\n\nEn cas d imprevu, merci de nous contacter des que possible.\n\nA demain,\n' + row.praticien;
    const sms = 'Rappel RDV : ' + row.prenom + ' ' + row.nom + ', demain a ' + row.heure + ' chez ' + row.praticien + '. En cas d imprevu merci de contacter le cabinet.';
    results.push({ json: { ...row, row_index: i + 2, email_subject: subject, email_body: body, sms_body: sms } });
  }
}
return results.length > 0 ? results : [{ json: { _skip: true } }];
