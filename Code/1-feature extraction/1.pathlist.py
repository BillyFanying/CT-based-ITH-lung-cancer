# 此代码输出t1的文件夹路径
#-*- coding: utf-8 -*-
import os
import json
import pandas as pd
import xlsxwriter
# with open("pathlist_T1_20200402.json",'r') as load_f:
#     pathlist = json.load(load_f)
#     print(pathlist)






def pathlist_output(path):

    pathlist = []
    count = 0
    subdir1 = os.listdir(path)  # EGFR
    for subdir1_num in subdir1:
        if subdir1_num == 'test':
            subdir2 = os.listdir(os.path.join(path, subdir1_num))  # 第二级子目录，每个病人姓名文件夹

            for subdir2_num in subdir2:
                if 'n' in subdir2_num:
                    subdir3 = os.listdir(os.path.join(path, subdir1_num, subdir2_num))  # 第三级子目录，部位文件
                    for subdir3_num in subdir3:
                        if 'T2W' in subdir3_num:  # 40_20 是t1,2_20是t2
                            path_print = os.path.join(path, subdir1_num, subdir2_num, subdir3_num)
                            print("r'" + path_print + "'" + ",")
                            pathlist.append(path_print)
                            count = count + 1


    return pathlist,count




if __name__=='__main__':
    final_pathlist = []
    countt = 0
    path = [r"E:/Mouse/"]
    for n in path:
        pathlist,count= pathlist_output(n)
        for path in pathlist:
            final_pathlist.append(path)
    print("共有" + str(len(final_pathlist)) + "人")

    #
    ### 以下为Gabor滤波后路径输出代码

    # for path in pathlist:
    #
    #     for i in range(1,21):
    #         final_path= os.path.join( path,'group%s' %i )
    #         final_pathlist.append(final_path)
    #         print("r'"+final_path+"'"+",")CE
    #         countt+=1
    # print(countt)
    print('****************路径输出完成*************')
    with open("I:/Chunna Yang_Project/2.PET/E_brain_experiment/T2W_Response.json","w") as f:
        json.dump(final_pathlist,f)
        print("加载入文件完成...")
    df_result = pd.DataFrame(pathlist)

    filepath = 'I:/Chunna Yang_Project/2.PET/E_brain_experiment/T2W_Response.xlsx'
    writer = pd.ExcelWriter(filepath)
    df_result.to_excel(excel_writer=writer,index=False,sheet_name='Sheet1')
    writer._save()