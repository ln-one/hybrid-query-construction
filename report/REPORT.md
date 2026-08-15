# 正式实验结果报告

> 本报告只读取真实逐查询记录；开发、held-out、鲁棒性与规模结果必须按 track 分开解释。

## 数据完整性

- 逐查询×方法×生成重复结果：665,376 条
- 独立查询单元：3,976 条
- 数据集：11 个
- 方法：11 个
- 生成失败回退率：0.0413%

## Controlled 主结果（数据集等权）

| method                 |   ndcg_at_10 |   recall_at_20 |   dense_depth |   sparse_depth |
|:-----------------------|-------------:|---------------:|--------------:|---------------:|
| bridge_shared          |       0.3357 |         0.5197 |      705.4300 |       705.0218 |
| dense_only             |       0.3347 |         0.5184 |     1095.8900 |      1033.7424 |
| mugi_controlled        |       0.3317 |         0.5155 |      938.6964 |       937.7676 |
| original               |       0.3325 |         0.5142 |     1278.1586 |      1228.4187 |
| proposed               |       0.3446 |         0.5258 |      701.4745 |       678.2360 |
| sparse_boolean_mask    |       0.3356 |         0.5201 |      731.5195 |       711.0645 |
| sparse_only            |       0.3439 |         0.5242 |      916.3674 |       882.7791 |
| sparse_references_only |       0.3203 |         0.5088 |     1141.7011 |      1136.7864 |

### 主结果的查询级分层 bootstrap 95% 区间

| method                 | metric       |   estimate |   ci95_lower |   ci95_upper |
|:-----------------------|:-------------|-----------:|-------------:|-------------:|
| bridge_shared          | ndcg_at_10   |     0.3357 |       0.3174 |       0.3535 |
| bridge_shared          | recall_at_20 |     0.5197 |       0.5011 |       0.5380 |
| bridge_shared          | dense_depth  |   705.4300 |     501.7036 |     988.7809 |
| bridge_shared          | sparse_depth |   705.0218 |     501.2824 |     988.3919 |
| dense_only             | ndcg_at_10   |     0.3347 |       0.3170 |       0.3520 |
| dense_only             | recall_at_20 |     0.5184 |       0.4995 |       0.5373 |
| dense_only             | dense_depth  |  1095.8900 |     785.1380 |    1616.5167 |
| dense_only             | sparse_depth |  1033.7424 |     730.8788 |    1546.2024 |
| mugi_controlled        | ndcg_at_10   |     0.3317 |       0.3133 |       0.3497 |
| mugi_controlled        | recall_at_20 |     0.5155 |       0.4972 |       0.5337 |
| mugi_controlled        | dense_depth  |   938.6964 |     579.4184 |    1429.4478 |
| mugi_controlled        | sparse_depth |   937.7676 |     578.7974 |    1428.0072 |
| original               | ndcg_at_10   |     0.3325 |       0.3144 |       0.3502 |
| original               | recall_at_20 |     0.5142 |       0.4952 |       0.5334 |
| original               | dense_depth  |  1278.1586 |     774.5939 |    2180.7996 |
| original               | sparse_depth |  1228.4187 |     731.8756 |    2126.3808 |
| proposed               | ndcg_at_10   |     0.3446 |       0.3266 |       0.3621 |
| proposed               | recall_at_20 |     0.5258 |       0.5073 |       0.5445 |
| proposed               | dense_depth  |   701.4745 |     482.3792 |    1045.5251 |
| proposed               | sparse_depth |   678.2360 |     461.2040 |    1020.2570 |
| sparse_boolean_mask    | ndcg_at_10   |     0.3356 |       0.3175 |       0.3534 |
| sparse_boolean_mask    | recall_at_20 |     0.5201 |       0.5016 |       0.5383 |
| sparse_boolean_mask    | dense_depth  |   731.5195 |     516.0336 |    1030.8114 |
| sparse_boolean_mask    | sparse_depth |   711.0645 |     496.7644 |    1009.4837 |
| sparse_only            | ndcg_at_10   |     0.3439 |       0.3256 |       0.3621 |
| sparse_only            | recall_at_20 |     0.5242 |       0.5061 |       0.5426 |
| sparse_only            | dense_depth  |   916.3674 |     606.5665 |    1429.7861 |
| sparse_only            | sparse_depth |   882.7791 |     577.1169 |    1394.6164 |
| sparse_references_only | ndcg_at_10   |     0.3203 |       0.3031 |       0.3375 |
| sparse_references_only | recall_at_20 |     0.5088 |       0.4908 |       0.5268 |
| sparse_references_only | dense_depth  |  1141.7011 |     773.9728 |    1603.6190 |
| sparse_references_only | sparse_depth |  1136.7864 |     770.6685 |    1597.0005 |

## Held-out 各数据集主结果

| dataset          | method                 |   ndcg_at_10 |   recall_at_20 |   dense_depth |   sparse_depth |   sparse_support |   sparse_exhaustion_rate |   fallback_rate |
|:-----------------|:-----------------------|-------------:|---------------:|--------------:|---------------:|-----------------:|-------------------------:|----------------:|
| arguana          | bridge_shared          |       0.4004 |         0.9265 |      123.4279 |       123.0071 |        8616.8049 |                   0.0000 |          0.0002 |
| arguana          | dense_only             |       0.3956 |         0.9194 |      164.6920 |       164.2620 |        8587.8300 |                   0.0000 |          0.0002 |
| arguana          | mugi_controlled        |       0.3843 |         0.9109 |      153.2316 |       152.7634 |        7508.7698 |                   0.0005 |          0.0002 |
| arguana          | original               |       0.3941 |         0.9203 |      157.1010 |       156.6629 |        8587.8300 |                   0.0000 |          0.0000 |
| arguana          | proposed               |       0.3991 |         0.9237 |      133.1432 |       132.7219 |        8587.8300 |                   0.0000 |          0.0002 |
| arguana          | sparse_boolean_mask    |       0.4005 |         0.9265 |      123.3931 |       122.9723 |        8587.8300 |                   0.0000 |          0.0002 |
| arguana          | sparse_only            |       0.3978 |         0.9241 |      126.8585 |       126.4260 |        8587.8300 |                   0.0000 |          0.0002 |
| arguana          | sparse_references_only |       0.3844 |         0.9109 |      153.2376 |       152.7693 |        7508.7698 |                   0.0005 |          0.0002 |
| fiqa             | bridge_shared          |       0.3635 |         0.5391 |     1104.0545 |      1103.5874 |       46673.3472 |                   0.0000 |          0.0000 |
| fiqa             | dense_only             |       0.3644 |         0.5306 |     2242.5540 |      2094.6698 |       28384.5679 |                   0.0201 |          0.0000 |
| fiqa             | mugi_controlled        |       0.3581 |         0.5376 |     1305.0093 |      1302.5057 |       45366.1656 |                   0.0015 |          0.0000 |
| fiqa             | original               |       0.3649 |         0.5260 |     2178.9568 |      2076.3302 |       28384.5679 |                   0.0123 |          0.0000 |
| fiqa             | proposed               |       0.3780 |         0.5450 |     1096.1996 |      1065.5885 |       28384.5679 |                   0.0093 |          0.0000 |
| fiqa             | sparse_boolean_mask    |       0.3627 |         0.5402 |     1128.4388 |      1104.9182 |       28384.5679 |                   0.0103 |          0.0000 |
| fiqa             | sparse_only            |       0.3806 |         0.5447 |     1432.4213 |      1361.6862 |       28384.5679 |                   0.0118 |          0.0000 |
| fiqa             | sparse_references_only |       0.3444 |         0.5298 |     1638.2469 |      1619.7726 |       42777.6991 |                   0.0041 |          0.0000 |
| scidocs          | bridge_shared          |       0.1905 |         0.2790 |      372.7137 |       372.2207 |       23239.6003 |                   0.0000 |          0.0000 |
| scidocs          | dense_only             |       0.1937 |         0.2757 |      645.5453 |       545.7453 |       11503.0310 |                   0.0233 |          0.0000 |
| scidocs          | mugi_controlled        |       0.1891 |         0.2767 |      404.2453 |       403.7607 |       23145.2300 |                   0.0000 |          0.0000 |
| scidocs          | original               |       0.1923 |         0.2721 |      694.8010 |       599.2940 |       11503.0310 |                   0.0270 |          0.0000 |
| scidocs          | proposed               |       0.1940 |         0.2787 |      448.7730 |       387.2253 |       11503.0310 |                   0.0163 |          0.0000 |
| scidocs          | sparse_boolean_mask    |       0.1902 |         0.2784 |      398.3347 |       340.7143 |       11503.0310 |                   0.0110 |          0.0000 |
| scidocs          | sparse_only            |       0.1939 |         0.2750 |      558.5163 |       495.6710 |       11503.0310 |                   0.0210 |          0.0000 |
| scidocs          | sparse_references_only |       0.1868 |         0.2747 |      412.2450 |       411.7670 |       23057.6437 |                   0.0000 |          0.0000 |
| webis-touche2020 | bridge_shared          |       0.3883 |         0.3344 |     1221.5238 |      1221.2721 |      284676.9524 |                   0.0000 |          0.0000 |
| webis-touche2020 | dense_only             |       0.3852 |         0.3478 |     1330.7687 |      1330.2925 |      151619.0408 |                   0.0000 |          0.0000 |
| webis-touche2020 | mugi_controlled        |       0.3953 |         0.3369 |     1892.2993 |      1892.0408 |      284240.3333 |                   0.0000 |          0.0000 |
| webis-touche2020 | original               |       0.3786 |         0.3382 |     2081.7755 |      2081.3878 |      151619.0408 |                   0.0000 |          0.0000 |
| webis-touche2020 | proposed               |       0.4071 |         0.3560 |     1127.7823 |      1127.4082 |      151618.8707 |                   0.0000 |          0.0000 |
| webis-touche2020 | sparse_boolean_mask    |       0.3890 |         0.3354 |     1275.9116 |      1275.6531 |      151618.8707 |                   0.0000 |          0.0000 |
| webis-touche2020 | sparse_only            |       0.4034 |         0.3531 |     1547.6735 |      1547.3333 |      151618.8707 |                   0.0000 |          0.0000 |
| webis-touche2020 | sparse_references_only |       0.3656 |         0.3199 |     2363.0748 |      2362.8367 |      267666.0612 |                   0.0000 |          0.0000 |

## 2×2 机制实验（数据集等权）

| method      |   ndcg_at_10 |   recall_at_20 |   dense_depth |   sparse_depth |
|:------------|-------------:|---------------:|--------------:|---------------:|
| dense_only  |       0.3347 |         0.5184 |     1095.8900 |      1033.7424 |
| original    |       0.3325 |         0.5142 |     1278.1586 |      1228.4187 |
| proposed    |       0.3446 |         0.5258 |      701.4745 |       678.2360 |
| sparse_only |       0.3439 |         0.5242 |      916.3674 |       882.7791 |

## 相对 Original 的访问变化

| dataset          | method                 |   dense_total_reduction_pct |   sparse_total_reduction_pct |   dual_depth_improvement_rate |
|:-----------------|:-----------------------|----------------------------:|-----------------------------:|------------------------------:|
| arguana          | bridge_shared          |                      21.434 |                       21.483 |                         0.635 |
| arguana          | dense_only             |                      -4.832 |                       -4.851 |                         0.325 |
| arguana          | mugi_controlled        |                       2.463 |                        2.489 |                         0.455 |
| arguana          | original               |                       0.000 |                        0.000 |                         0.000 |
| arguana          | proposed               |                      15.250 |                       15.282 |                         0.615 |
| arguana          | sparse_boolean_mask    |                      21.456 |                       21.505 |                         0.635 |
| arguana          | sparse_only            |                      19.250 |                       19.301 |                         0.673 |
| arguana          | sparse_references_only |                       2.459 |                        2.485 |                         0.455 |
| fiqa             | bridge_shared          |                      49.331 |                       46.849 |                         0.674 |
| fiqa             | dense_only             |                      -2.919 |                       -0.883 |                         0.466 |
| fiqa             | mugi_controlled        |                      40.109 |                       37.269 |                         0.653 |
| fiqa             | original               |                       0.000 |                        0.000 |                         0.000 |
| fiqa             | proposed               |                      49.692 |                       48.679 |                         0.748 |
| fiqa             | sparse_boolean_mask    |                      48.212 |                       46.785 |                         0.657 |
| fiqa             | sparse_only            |                      34.261 |                       34.419 |                         0.671 |
| fiqa             | sparse_references_only |                      24.815 |                       21.989 |                         0.574 |
| scidocs          | bridge_shared          |                      46.357 |                       37.890 |                         0.683 |
| scidocs          | dense_only             |                       7.089 |                        8.935 |                         0.497 |
| scidocs          | mugi_controlled        |                      41.819 |                       32.627 |                         0.651 |
| scidocs          | original               |                       0.000 |                        0.000 |                         0.000 |
| scidocs          | proposed               |                      35.410 |                       35.386 |                         0.718 |
| scidocs          | sparse_boolean_mask    |                      42.669 |                       43.147 |                         0.679 |
| scidocs          | sparse_only            |                      19.615 |                       17.291 |                         0.688 |
| scidocs          | sparse_references_only |                      40.667 |                       31.291 |                         0.591 |
| webis-touche2020 | bridge_shared          |                      41.323 |                       41.324 |                         0.306 |
| webis-touche2020 | dense_only             |                      36.075 |                       36.086 |                         0.531 |
| webis-touche2020 | mugi_controlled        |                       9.102 |                        9.097 |                         0.306 |
| webis-touche2020 | original               |                       0.000 |                        0.000 |                         0.000 |
| webis-touche2020 | proposed               |                      45.826 |                       45.834 |                         0.408 |
| webis-touche2020 | sparse_boolean_mask    |                      38.710 |                       38.711 |                         0.286 |
| webis-touche2020 | sparse_only            |                      25.656 |                       25.659 |                         0.327 |
| webis-touche2020 | sparse_references_only |                     -13.512 |                      -13.522 |                         0.204 |

### 数据集等权访问变化及 95% 区间

| dataset             | method                 | metric                      |   estimate |   ci95_lower |   ci95_upper |
|:--------------------|:-----------------------|:----------------------------|-----------:|-------------:|-------------:|
| macro_equal_dataset | bridge_shared          | dense_total_reduction_pct   |    39.6112 |      -4.1662 |      46.8209 |
| macro_equal_dataset | bridge_shared          | dual_depth_improvement_rate |     0.5747 |       0.5404 |       0.6105 |
| macro_equal_dataset | bridge_shared          | sparse_total_reduction_pct  |    36.8866 |      -6.9060 |      44.2383 |
| macro_equal_dataset | dense_only             | dense_total_reduction_pct   |     8.8535 |      -4.6312 |      12.5311 |
| macro_equal_dataset | dense_only             | dual_depth_improvement_rate |     0.4547 |       0.4172 |       0.4927 |
| macro_equal_dataset | dense_only             | sparse_total_reduction_pct  |     9.8219 |      -3.4626 |      13.2423 |
| macro_equal_dataset | mugi_controlled        | dense_total_reduction_pct   |    23.3729 |    -121.9421 |      36.8303 |
| macro_equal_dataset | mugi_controlled        | dual_depth_improvement_rate |     0.5163 |       0.4819 |       0.5524 |
| macro_equal_dataset | mugi_controlled        | sparse_total_reduction_pct  |    20.3706 |    -125.1855 |      34.0251 |
| macro_equal_dataset | original               | dense_total_reduction_pct   |     0.0000 |       0.0000 |       0.0000 |
| macro_equal_dataset | original               | dual_depth_improvement_rate |     0.0000 |       0.0000 |       0.0000 |
| macro_equal_dataset | original               | sparse_total_reduction_pct  |     0.0000 |       0.0000 |       0.0000 |
| macro_equal_dataset | proposed               | dense_total_reduction_pct   |    36.5443 |       8.2144 |      41.7297 |
| macro_equal_dataset | proposed               | dual_depth_improvement_rate |     0.6223 |       0.5858 |       0.6600 |
| macro_equal_dataset | proposed               | sparse_total_reduction_pct  |    36.2953 |       8.1152 |      41.2003 |
| macro_equal_dataset | sparse_boolean_mask    | dense_total_reduction_pct   |    37.7620 |      -6.7757 |      45.1633 |
| macro_equal_dataset | sparse_boolean_mask    | dual_depth_improvement_rate |     0.5643 |       0.5308 |       0.5995 |
| macro_equal_dataset | sparse_boolean_mask    | sparse_total_reduction_pct  |    37.5373 |      -6.8569 |      44.6504 |
| macro_equal_dataset | sparse_only            | dense_total_reduction_pct   |    24.6956 |      -4.2522 |      30.0230 |
| macro_equal_dataset | sparse_only            | dual_depth_improvement_rate |     0.5897 |       0.5549 |       0.6260 |
| macro_equal_dataset | sparse_only            | sparse_total_reduction_pct  |    24.1672 |      -4.5651 |      29.2063 |
| macro_equal_dataset | sparse_references_only | dense_total_reduction_pct   |    13.6073 |    -148.0230 |      29.7102 |
| macro_equal_dataset | sparse_references_only | dual_depth_improvement_rate |     0.4561 |       0.4256 |       0.4896 |
| macro_equal_dataset | sparse_references_only | sparse_total_reduction_pct  |    10.5608 |    -151.2494 |      26.6153 |

## 预注册主比较

| comparison                | metric       |   favorable_difference |   ci95_lower |   ci95_upper |    p_raw |   p_holm |
|:--------------------------|:-------------|-----------------------:|-------------:|-------------:|---------:|---------:|
| proposed_vs_original      | ndcg_at_10   |               0.012083 |     0.003387 |     0.020830 | 0.006399 | 0.006399 |
| proposed_vs_original      | recall_at_20 |               0.011673 |     0.005681 |     0.017967 | 0.000200 | 0.000400 |
| proposed_vs_original      | dense_depth  |             576.684050 |   232.609645 |  1188.938639 | 0.000100 | 0.000400 |
| proposed_vs_original      | sparse_depth |             550.182749 |   207.190069 |  1159.707903 | 0.000100 | 0.000400 |
| proposed_vs_bridge_shared | ndcg_at_10   |               0.008919 |     0.004571 |     0.013334 | 0.000100 | 0.000400 |
| proposed_vs_bridge_shared | recall_at_20 |               0.006095 |     0.001364 |     0.011184 | 0.018598 | 0.055794 |
| proposed_vs_bridge_shared | dense_depth  |               3.955458 |   -93.434345 |    83.375403 | 0.946805 | 1.000000 |
| proposed_vs_bridge_shared | sparse_depth |              26.785864 |   -69.681588 |   104.512456 | 0.611739 | 1.000000 |

### 结论分类

| comparison                | classification   | rule                 |
|:--------------------------|:-----------------|:---------------------|
| proposed_vs_bridge_shared | 混合               | 四项有利差值的95%区间同向，否则为混合 |
| proposed_vs_original      | 强阳性              | 四项有利差值的95%区间同向，否则为混合 |

## 公开方法完整复现

下表将各论文对应的提示词与整合规则同冻结的 Original 和 Proposed 并列展示；该表为描述性完整方法比较，预注册显著性检验仍只针对 controlled 主比较。

| source                           | method    |   ndcg_at_10 |   recall_at_20 |   dense_depth |   sparse_depth |
|:---------------------------------|:----------|-------------:|---------------:|--------------:|---------------:|
| frozen_primary_protocol          | original  |       0.3325 |         0.5142 |     1278.1586 |      1228.4187 |
| frozen_primary_protocol          | proposed  |       0.3446 |         0.5258 |      701.4745 |       678.2360 |
| published_prompt_and_integration | hyde      |       0.2956 |         0.4746 |     7918.3498 |      7536.6225 |
| published_prompt_and_integration | mugi      |       0.3264 |         0.5109 |     1409.0139 |      1406.3202 |
| published_prompt_and_integration | query2doc |       0.3461 |         0.5229 |      864.9801 |       857.8034 |

## 消融与敏感性

### 参考文本数量

|   reference_count |   ndcg_at_10 |   recall_at_20 |   dense_depth |   sparse_depth |
|------------------:|-------------:|---------------:|--------------:|---------------:|
|            1.0000 |       0.3338 |         0.5173 |      925.6710 |       884.4496 |
|            3.0000 |       0.3423 |         0.5224 |      692.9036 |       660.3050 |
|            5.0000 |       0.3446 |         0.5258 |      701.4745 |       678.2360 |

### Sparse 算子

| method                 |   ndcg_at_10 |   recall_at_20 |   dense_depth |   sparse_depth |
|:-----------------------|-------------:|---------------:|--------------:|---------------:|
| proposed               |       0.3446 |         0.5258 |      701.4745 |       678.2360 |
| sparse_boolean_mask    |       0.3356 |         0.5201 |      731.5195 |       711.0645 |
| sparse_references_only |       0.3203 |         0.5088 |     1141.7011 |      1136.7864 |

### RRF 常数

|   rrf_constant |   ndcg_at_10 |   recall_at_20 |   dense_depth |   sparse_depth |
|---------------:|-------------:|---------------:|--------------:|---------------:|
|         2.0000 |       0.3591 |         0.5351 |     1091.6735 |      1050.1093 |
|        20.0000 |       0.3536 |         0.5354 |     1366.4157 |      1332.8745 |
|        60.0000 |       0.3446 |         0.5258 |      701.4745 |       678.2360 |
|       100.0000 |       0.3427 |         0.5181 |      337.4879 |       324.4998 |

### 固定 Top-L

| method        |   top_l |   ndcg_at_10 |   recall_at_20 |   complete_top20_exact_rate |
|:--------------|--------:|-------------:|---------------:|----------------------------:|
| bridge_shared |      10 |       0.3393 |         0.4993 |                      0.0000 |
| bridge_shared |      20 |       0.3360 |         0.5235 |                      0.0007 |
| bridge_shared |      50 |       0.3336 |         0.5205 |                      0.1679 |
| bridge_shared |     100 |       0.3338 |         0.5119 |                      0.4772 |
| bridge_shared |     200 |       0.3353 |         0.5166 |                      0.7454 |
| bridge_shared |     500 |       0.3354 |         0.5194 |                      0.8907 |
| bridge_shared |    1000 |       0.3356 |         0.5196 |                      0.9252 |
| original      |      10 |       0.3400 |         0.4929 |                      0.0000 |
| original      |      20 |       0.3373 |         0.5191 |                      0.0004 |
| original      |      50 |       0.3288 |         0.5123 |                      0.1519 |
| original      |     100 |       0.3303 |         0.5064 |                      0.4423 |
| original      |     200 |       0.3321 |         0.5090 |                      0.6886 |
| original      |     500 |       0.3325 |         0.5127 |                      0.8459 |
| original      |    1000 |       0.3324 |         0.5137 |                      0.8998 |
| proposed      |      10 |       0.3537 |         0.5069 |                      0.0000 |
| proposed      |      20 |       0.3484 |         0.5308 |                      0.0005 |
| proposed      |      50 |       0.3417 |         0.5264 |                      0.1704 |
| proposed      |     100 |       0.3427 |         0.5176 |                      0.4856 |
| proposed      |     200 |       0.3437 |         0.5212 |                      0.7508 |
| proposed      |     500 |       0.3440 |         0.5255 |                      0.8982 |
| proposed      |    1000 |       0.3446 |         0.5260 |                      0.9309 |

## 鲁棒性：第二生成模型与第二 Dense 编码器

| condition_id   | dataset          |   original_ndcg |   proposed_ndcg |   delta_ndcg |   original_recall |   proposed_recall |   delta_recall |   dense_reduction_pct |   sparse_reduction_pct |   proposed_fallback_rate |
|:---------------|:-----------------|----------------:|----------------:|-------------:|------------------:|------------------:|---------------:|----------------------:|-----------------------:|-------------------------:|
| contriever     | arguana          |          0.3514 |          0.3622 |       0.0108 |            0.8798 |            0.8988 |         0.0190 |                9.5306 |                 9.5496 |                   0.0002 |
| contriever     | fiqa             |          0.2477 |          0.2687 |       0.0210 |            0.4092 |            0.4348 |         0.0256 |                5.5613 |                 4.7948 |                   0.0000 |
| contriever     | scidocs          |          0.1650 |          0.1709 |       0.0060 |            0.2374 |            0.2507 |         0.0133 |               30.1891 |                29.7133 |                   0.0000 |
| contriever     | webis-touche2020 |          0.2200 |          0.2521 |       0.0322 |            0.2431 |            0.2852 |         0.0421 |              -14.2937 |                -4.3437 |                   0.0000 |
| mistral        | arguana          |          0.3674 |          0.3830 |       0.0156 |            0.9000 |            0.9000 |         0.0000 |                7.1246 |                 7.1618 |                   0.1000 |
| mistral        | fiqa             |          0.2946 |          0.3178 |       0.0232 |            0.4513 |            0.4790 |         0.0278 |               45.2717 |                44.8361 |                   0.0000 |
| mistral        | scidocs          |          0.1799 |          0.1858 |       0.0059 |            0.2780 |            0.2988 |         0.0208 |               15.6215 |                17.0002 |                   0.0000 |
| mistral        | webis-touche2020 |          0.3786 |          0.3890 |       0.0103 |            0.3382 |            0.3488 |         0.0106 |               47.6147 |                47.6216 |                   0.0000 |

以下条件出现访问深度恶化（负百分比表示读取更多）：contriever/webis-touche2020：Dense -14.29%，Sparse -4.34%。

## 规模趋势

| dataset           |   documents |   original_ndcg |   proposed_ndcg |   delta_ndcg |   original_recall |   proposed_recall |   delta_recall |   dense_reduction_pct |   sparse_reduction_pct |   proposed_fallback_rate |
|:------------------|------------:|----------------:|----------------:|-------------:|------------------:|------------------:|---------------:|----------------------:|-----------------------:|-------------------------:|
| trec-covid-25000  |       25000 |          0.8292 |          0.8613 |       0.0321 |            0.0458 |            0.0483 |         0.0025 |               68.1230 |                68.1590 |                   0.0000 |
| trec-covid-50000  |       50000 |          0.8184 |          0.8486 |       0.0302 |            0.0443 |            0.0469 |         0.0026 |               65.1121 |                65.1374 |                   0.0000 |
| trec-covid-100000 |      100000 |          0.7930 |          0.8388 |       0.0458 |            0.0416 |            0.0450 |         0.0034 |               79.8270 |                79.8391 |                   0.0000 |
| trec-covid-171332 |      171332 |          0.7781 |          0.8224 |       0.0443 |            0.0398 |            0.0435 |         0.0037 |               74.8865 |                66.7149 |                   0.0000 |

## 开发集机制检查（不用于 held-out 主结论）

| dataset    |   original_ndcg |   proposed_ndcg |   delta_ndcg |   original_recall |   proposed_recall |   delta_recall |   dense_reduction_pct |   sparse_reduction_pct |   proposed_fallback_rate |
|:-----------|----------------:|----------------:|-------------:|------------------:|------------------:|---------------:|----------------------:|-----------------------:|-------------------------:|
| nfcorpus   |          0.3670 |          0.3793 |       0.0124 |            0.2099 |            0.2195 |         0.0096 |               15.0331 |                23.1514 |                   0.0000 |
| scifact    |          0.7253 |          0.7427 |       0.0174 |            0.9036 |            0.9200 |         0.0164 |               22.1789 |                20.8971 |                   0.0000 |
| trec-covid |          0.7781 |          0.8224 |       0.0443 |            0.0398 |            0.0435 |         0.0037 |               74.8865 |                66.7149 |                   0.0000 |

## 生成成本

| dataset          | model_id                           | prompt_path                              |   records |   mean_prompt_tokens |   mean_completion_tokens |   mean_attempts |   failure_rate |
|:-----------------|:-----------------------------------|:-----------------------------------------|----------:|---------------------:|-------------------------:|----------------:|---------------:|
| arguana          | Qwen/Qwen2.5-7B-Instruct           | prompts/baselines/hyde-arguana-v1.txt    |      4218 |              316.689 |                   92.070 |           1.000 |          0.000 |
| arguana          | Qwen/Qwen2.5-7B-Instruct           | prompts/baselines/mugi-v1.txt            |      4218 |              341.531 |                   78.902 |           1.003 |          0.000 |
| arguana          | Qwen/Qwen2.5-7B-Instruct           | prompts/baselines/query2doc-v1.txt       |      4218 |              309.789 |                   41.052 |           1.000 |          0.000 |
| arguana          | Qwen/Qwen2.5-7B-Instruct           | prompts/primary-reference-v1.txt         |      4218 |              413.367 |                   76.051 |           1.001 |          0.000 |
| arguana          | mistralai/Mistral-7B-Instruct-v0.3 | prompts/primary-reference-v1.txt         |       300 |              597.690 |                  207.920 |           1.213 |          0.100 |
| fiqa             | Qwen/Qwen2.5-7B-Instruct           | prompts/baselines/hyde-fiqa-v1.txt       |      1944 |               78.178 |                   93.940 |           1.003 |          0.002 |
| fiqa             | Qwen/Qwen2.5-7B-Instruct           | prompts/baselines/mugi-v1.txt            |      1944 |              103.459 |                   60.881 |           1.004 |          0.002 |
| fiqa             | Qwen/Qwen2.5-7B-Instruct           | prompts/baselines/query2doc-v1.txt       |      1944 |               73.243 |                   37.816 |           1.004 |          0.002 |
| fiqa             | Qwen/Qwen2.5-7B-Instruct           | prompts/primary-reference-v1.txt         |      1944 |              175.506 |                   68.604 |           1.000 |          0.000 |
| fiqa             | mistralai/Mistral-7B-Instruct-v0.3 | prompts/primary-reference-v1.txt         |       300 |              201.490 |                  135.843 |           1.017 |          0.000 |
| nfcorpus         | Qwen/Qwen2.5-7B-Instruct           | prompts/baselines/hyde-v1.txt            |       969 |               76.832 |                   88.755 |           1.003 |          0.001 |
| nfcorpus         | Qwen/Qwen2.5-7B-Instruct           | prompts/baselines/mugi-v1.txt            |       969 |               95.038 |                   65.878 |           1.003 |          0.002 |
| nfcorpus         | Qwen/Qwen2.5-7B-Instruct           | prompts/baselines/query2doc-v1.txt       |       969 |               64.316 |                   31.953 |           1.000 |          0.000 |
| nfcorpus         | Qwen/Qwen2.5-7B-Instruct           | prompts/primary-reference-v1.txt         |       969 |              167.316 |                   66.052 |           1.000 |          0.000 |
| scidocs          | Qwen/Qwen2.5-7B-Instruct           | prompts/baselines/hyde-v1.txt            |      3000 |               83.377 |                   82.031 |           1.001 |          0.000 |
| scidocs          | Qwen/Qwen2.5-7B-Instruct           | prompts/baselines/mugi-v1.txt            |      3000 |              102.328 |                   63.393 |           1.000 |          0.000 |
| scidocs          | Qwen/Qwen2.5-7B-Instruct           | prompts/baselines/query2doc-v1.txt       |      3000 |               72.625 |                   37.411 |           1.002 |          0.000 |
| scidocs          | Qwen/Qwen2.5-7B-Instruct           | prompts/primary-reference-v1.txt         |      3000 |              175.337 |                   63.921 |           1.000 |          0.000 |
| scidocs          | mistralai/Mistral-7B-Instruct-v0.3 | prompts/primary-reference-v1.txt         |       300 |              196.863 |                  119.747 |           1.003 |          0.000 |
| scifact          | Qwen/Qwen2.5-7B-Instruct           | prompts/baselines/hyde-scifact-v1.txt    |       900 |               93.150 |                  119.633 |           1.003 |          0.000 |
| scifact          | Qwen/Qwen2.5-7B-Instruct           | prompts/baselines/mugi-v1.txt            |       900 |              108.843 |                   80.990 |           1.000 |          0.000 |
| scifact          | Qwen/Qwen2.5-7B-Instruct           | prompts/baselines/query2doc-v1.txt       |       900 |               78.843 |                   30.733 |           1.000 |          0.000 |
| scifact          | Qwen/Qwen2.5-7B-Instruct           | prompts/primary-reference-v1.txt         |       900 |              181.843 |                   85.386 |           1.000 |          0.000 |
| trec-covid       | Qwen/Qwen2.5-7B-Instruct           | prompts/baselines/hyde-trec-covid-v1.txt |       150 |               79.220 |                  104.320 |           1.000 |          0.000 |
| trec-covid       | Qwen/Qwen2.5-7B-Instruct           | prompts/baselines/mugi-v1.txt            |       150 |              104.220 |                   74.480 |           1.000 |          0.000 |
| trec-covid       | Qwen/Qwen2.5-7B-Instruct           | prompts/baselines/query2doc-v1.txt       |       150 |               76.773 |                   44.047 |           1.007 |          0.000 |
| trec-covid       | Qwen/Qwen2.5-7B-Instruct           | prompts/primary-reference-v1.txt         |       150 |              177.220 |                   79.380 |           1.000 |          0.000 |
| webis-touche2020 | Qwen/Qwen2.5-7B-Instruct           | prompts/baselines/hyde-v1.txt            |       147 |               77.878 |                   77.177 |           1.000 |          0.000 |
| webis-touche2020 | Qwen/Qwen2.5-7B-Instruct           | prompts/baselines/mugi-v1.txt            |       147 |               96.878 |                   57.524 |           1.000 |          0.000 |
| webis-touche2020 | Qwen/Qwen2.5-7B-Instruct           | prompts/baselines/query2doc-v1.txt       |       147 |               66.878 |                   33.497 |           1.000 |          0.000 |
| webis-touche2020 | Qwen/Qwen2.5-7B-Instruct           | prompts/primary-reference-v1.txt         |       147 |              169.878 |                   63.735 |           1.000 |          0.000 |
| webis-touche2020 | mistralai/Mistral-7B-Instruct-v0.3 | prompts/primary-reference-v1.txt         |       147 |              187.592 |                  126.102 |           1.000 |          0.000 |

## 结论边界

逻辑访问深度不等同于在线延迟；生成成本、表示构造、检索执行和融合回放分别核算。完整结果保留每个数据集与失败回退记录，不以总体均值隐藏混合或负面结果。
