import zipfile, csv, time, sys
from lxml import etree

ns = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
src = '/mnt/user-data/uploads/Veltris-Vehicle.xlsx'
out = '/home/claude/raw_data.csv'

z = zipfile.ZipFile(src)
f = z.open('xl/worksheets/sheet1.xml')

t0 = time.time()
n_rows = 0

with open(out, 'w', newline='') as fout:
    writer = csv.writer(fout)
    context = etree.iterparse(f, events=('end',), tag=ns+'row')
    for event, row_elem in context:
        vals = []
        for c in row_elem:
            v = c.find(ns+'v')
            if v is not None:
                vals.append(v.text)
            else:
                is_el = c.find(ns+'is')
                if is_el is not None:
                    t = is_el.find(ns+'t')
                    vals.append(t.text if t is not None else '')
                else:
                    vals.append('')
        writer.writerow(vals)
        n_rows += 1
        row_elem.clear()
        while row_elem.getprevious() is not None:
            del row_elem.getparent()[0]
        if n_rows % 50000 == 0:
            print(f'rows={n_rows} elapsed={time.time()-t0:.1f}s', flush=True)

print(f'DONE rows={n_rows} elapsed={time.time()-t0:.1f}s')
