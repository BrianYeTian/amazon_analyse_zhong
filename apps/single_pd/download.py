from io import BytesIO

import xlwt
from flask import make_response

from apps.single_pd.model import Trace_pd_info


def write_to_excel(id_list):
    pd_infos = id_list.split(',')
    print(pd_infos)

    col_name = ['asin', '售价', '评价数量', '星级', '排名', '目录', '库存', '市场', '时间']
    new = xlwt.Workbook(encoding='utf-8')
    sheet = new.add_sheet('新闻', cell_overwrite_ok=True)
    # 写上字段信息
    for field in range(0, len(col_name)):
        sheet.write(0, field, col_name[field])

    # 获取并写入数据段信息
    row = 1
    col = 0
    for row in range(1, len(pd_infos) + 1):
        pd_info = []
        pd = Trace_pd_info.query.filter_by(id=pd_infos[row - 1]).first()
        pd_info.append(pd.asin)
        pd_info.append(pd.price)
        pd_info.append(pd.rating_num)
        pd_info.append(pd.rating)
        pd_info.append(pd.rank)
        pd_info.append(pd.cate)
        pd_info.append(pd.inventory)
        pd_info.append(pd.market)
        pd_info.append(pd.update_date)
        print(pd_info)
        # print(new)
        for col in range(0, len(col_name)):
            sheet.write(row, col, u'%s' % pd_info[col])

    return new

