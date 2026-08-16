# 正式实验结果报告

> 本报告只读取真实逐查询记录；七个正式数据集等权汇总，鲁棒性与规模实验按 track 单独报告。

## 数据完整性

- 逐查询×方法×生成重复结果：665,376 条
- 独立查询单元：3,976 条
- 数据集：11 个
- 方法：11 个
- 生成失败回退率：0.0413%

## Controlled 主结果（数据集等权）

| method                 |   ndcg_at_10 |   recall_at_20 |   dense_depth |   sparse_depth |
|:-----------------------|-------------:|---------------:|--------------:|---------------:|
| bridge_shared          |       0.4671 |         0.4666 |      607.4491 |       606.7491 |
| dense_only             |       0.4621 |         0.4637 |     1386.5298 |      1219.9470 |
| mugi_controlled        |       0.4638 |         0.4635 |      741.5383 |       740.6521 |
| original               |       0.4572 |         0.4586 |     1752.4284 |      1455.1354 |
| proposed               |       0.4747 |         0.4695 |      728.8784 |       673.1993 |
| sparse_boolean_mask    |       0.4675 |         0.4660 |      626.1448 |       575.2442 |
| sparse_only            |       0.4714 |         0.4678 |      884.4407 |       822.0169 |
| sparse_references_only |       0.4565 |         0.4592 |      978.5421 |       974.8536 |

### 主结果的查询级分层 bootstrap 95% 区间

| method                 | metric       |   estimate |   ci95_lower |   ci95_upper |
|:-----------------------|:-------------|-----------:|-------------:|-------------:|
| bridge_shared          | ndcg_at_10   |     0.4671 |       0.4524 |       0.4815 |
| bridge_shared          | recall_at_20 |     0.4666 |       0.4548 |       0.4786 |
| bridge_shared          | dense_depth  |   607.4491 |     471.9635 |     786.9897 |
| bridge_shared          | sparse_depth |   606.7491 |     471.3599 |     786.1936 |
| dense_only             | ndcg_at_10   |     0.4621 |       0.4472 |       0.4768 |
| dense_only             | recall_at_20 |     0.4637 |       0.4515 |       0.4762 |
| dense_only             | dense_depth  |  1386.5298 |     903.9928 |    1982.4580 |
| dense_only             | sparse_depth |  1219.9470 |     805.9631 |    1731.0894 |
| mugi_controlled        | ndcg_at_10   |     0.4638 |       0.4490 |       0.4782 |
| mugi_controlled        | recall_at_20 |     0.4635 |       0.4517 |       0.4754 |
| mugi_controlled        | dense_depth  |   741.5383 |     523.5440 |    1040.3937 |
| mugi_controlled        | sparse_depth |   740.6521 |     522.5759 |    1039.5066 |
| original               | ndcg_at_10   |     0.4572 |       0.4420 |       0.4723 |
| original               | recall_at_20 |     0.4586 |       0.4460 |       0.4713 |
| original               | dense_depth  |  1752.4284 |     978.6922 |    2829.2113 |
| original               | sparse_depth |  1455.1354 |     899.2376 |    2165.0654 |
| proposed               | ndcg_at_10   |     0.4747 |       0.4602 |       0.4889 |
| proposed               | recall_at_20 |     0.4695 |       0.4575 |       0.4818 |
| proposed               | dense_depth  |   728.8784 |     496.1052 |    1033.7524 |
| proposed               | sparse_depth |   673.1993 |     440.5733 |     975.6937 |
| sparse_boolean_mask    | ndcg_at_10   |     0.4675 |       0.4528 |       0.4819 |
| sparse_boolean_mask    | recall_at_20 |     0.4660 |       0.4541 |       0.4780 |
| sparse_boolean_mask    | dense_depth  |   626.1448 |     485.0504 |     817.9495 |
| sparse_boolean_mask    | sparse_depth |   575.2442 |     433.9979 |     763.9098 |
| sparse_only            | ndcg_at_10   |     0.4714 |       0.4567 |       0.4862 |
| sparse_only            | recall_at_20 |     0.4678 |       0.4561 |       0.4799 |
| sparse_only            | dense_depth  |   884.4407 |     625.0972 |    1234.2828 |
| sparse_only            | sparse_depth |   822.0169 |     565.2146 |    1170.0314 |
| sparse_references_only | ndcg_at_10   |     0.4565 |       0.4418 |       0.4706 |
| sparse_references_only | recall_at_20 |     0.4592 |       0.4476 |       0.4710 |
| sparse_references_only | dense_depth  |   978.5421 |     732.2534 |    1282.8643 |
| sparse_references_only | sparse_depth |   974.8536 |     729.1148 |    1279.3796 |

## 七个正式数据集主结果

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
| nfcorpus         | bridge_shared          |       0.3780 |         0.2260 |      359.0537 |       357.5872 |        3211.5552 |                   0.0114 |          0.0000 |
| nfcorpus         | dense_only             |       0.3742 |         0.2172 |      507.3633 |       182.9329 |         561.5263 |                   0.5046 |          0.0000 |
| nfcorpus         | mugi_controlled        |       0.3779 |         0.2256 |      368.2590 |       367.6584 |        3211.1073 |                   0.0093 |          0.0000 |
| nfcorpus         | original               |       0.3670 |         0.2099 |      474.3715 |       173.7430 |         561.5263 |                   0.4861 |          0.0000 |
| nfcorpus         | proposed               |       0.3793 |         0.2195 |      403.0588 |       133.5191 |         561.5263 |                   0.4675 |          0.0000 |
| nfcorpus         | sparse_boolean_mask    |       0.3777 |         0.2203 |      376.4469 |       120.6945 |         561.5263 |                   0.4603 |          0.0000 |
| nfcorpus         | sparse_only            |       0.3714 |         0.2152 |      418.0599 |       143.6017 |         561.5263 |                   0.4582 |          0.0000 |
| nfcorpus         | sparse_references_only |       0.3762 |         0.2220 |      409.0660 |       406.2941 |        3204.1373 |                   0.0124 |          0.0000 |
| scidocs          | bridge_shared          |       0.1905 |         0.2790 |      372.7137 |       372.2207 |       23239.6003 |                   0.0000 |          0.0000 |
| scidocs          | dense_only             |       0.1937 |         0.2757 |      645.5453 |       545.7453 |       11503.0310 |                   0.0233 |          0.0000 |
| scidocs          | mugi_controlled        |       0.1891 |         0.2767 |      404.2453 |       403.7607 |       23145.2300 |                   0.0000 |          0.0000 |
| scidocs          | original               |       0.1923 |         0.2721 |      694.8010 |       599.2940 |       11503.0310 |                   0.0270 |          0.0000 |
| scidocs          | proposed               |       0.1940 |         0.2787 |      448.7730 |       387.2253 |       11503.0310 |                   0.0163 |          0.0000 |
| scidocs          | sparse_boolean_mask    |       0.1902 |         0.2784 |      398.3347 |       340.7143 |       11503.0310 |                   0.0110 |          0.0000 |
| scidocs          | sparse_only            |       0.1939 |         0.2750 |      558.5163 |       495.6710 |       11503.0310 |                   0.0210 |          0.0000 |
| scidocs          | sparse_references_only |       0.1868 |         0.2747 |      412.2450 |       411.7670 |       23057.6437 |                   0.0000 |          0.0000 |
| scifact          | bridge_shared          |       0.7325 |         0.9182 |      284.0633 |       282.6422 |        4489.0389 |                   0.0033 |          0.0000 |
| scifact          | dense_only             |       0.7360 |         0.9136 |      413.8056 |       369.0467 |        2765.6733 |                   0.0511 |          0.0000 |
| scifact          | mugi_controlled        |       0.7295 |         0.9138 |      293.5633 |       292.0289 |        4421.7278 |                   0.0056 |          0.0000 |
| scifact          | original               |       0.7253 |         0.9036 |      409.0733 |       368.5900 |        2765.6733 |                   0.0433 |          0.0000 |
| scifact          | proposed               |       0.7427 |         0.9200 |      318.3456 |       291.5656 |        2765.6733 |                   0.0389 |          0.0000 |
| scifact          | sparse_boolean_mask    |       0.7333 |         0.9182 |      292.0289 |       273.6433 |        2765.6733 |                   0.0300 |          0.0000 |
| scifact          | sparse_only            |       0.7345 |         0.9192 |      331.1822 |       303.3200 |        2765.6733 |                   0.0356 |          0.0000 |
| scifact          | sparse_references_only |       0.7313 |         0.9149 |      302.4844 |       299.3956 |        4382.9633 |                   0.0078 |          0.0000 |
| trec-covid       | bridge_shared          |       0.8169 |         0.0433 |      787.3067 |       786.9267 |      141483.1467 |                   0.0000 |          0.0000 |
| trec-covid       | dense_only             |       0.7856 |         0.0413 |     4400.9800 |      3852.6800 |       92683.7800 |                   0.0133 |          0.0000 |
| trec-covid       | mugi_controlled        |       0.8123 |         0.0434 |      774.1600 |       773.8067 |      139837.5133 |                   0.0000 |          0.0000 |
| trec-covid       | original               |       0.7781 |         0.0398 |     6270.9200 |      4729.9400 |       92683.7800 |                   0.0200 |          0.0000 |
| trec-covid       | proposed               |       0.8224 |         0.0435 |     1574.8467 |      1574.3667 |       92683.7800 |                   0.0000 |          0.0000 |
| trec-covid       | sparse_boolean_mask    |       0.8190 |         0.0432 |      788.4600 |       788.1133 |       92683.7800 |                   0.0000 |          0.0000 |
| trec-covid       | sparse_only            |       0.8183 |         0.0431 |     1776.3733 |      1776.0800 |       92683.7800 |                   0.0000 |          0.0000 |
| trec-covid       | sparse_references_only |       0.8067 |         0.0426 |     1571.4400 |      1571.1400 |      136313.4000 |                   0.0000 |          0.0000 |
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
| dense_only  |       0.4621 |         0.4637 |     1386.5298 |      1219.9470 |
| original    |       0.4572 |         0.4586 |     1752.4284 |      1455.1354 |
| proposed    |       0.4747 |         0.4695 |      728.8784 |       673.1993 |
| sparse_only |       0.4714 |         0.4678 |      884.4407 |       822.0169 |

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
| nfcorpus         | bridge_shared          |                      24.310 |                     -105.814 |                         0.412 |
| nfcorpus         | dense_only             |                      -6.955 |                       -5.289 |                         0.201 |
| nfcorpus         | mugi_controlled        |                      22.369 |                     -111.610 |                         0.418 |
| nfcorpus         | original               |                       0.000 |                        0.000 |                         0.000 |
| nfcorpus         | proposed               |                      15.033 |                       23.151 |                         0.402 |
| nfcorpus         | sparse_boolean_mask    |                      20.643 |                       30.533 |                         0.390 |
| nfcorpus         | sparse_only            |                      11.871 |                       17.348 |                         0.390 |
| nfcorpus         | sparse_references_only |                      13.767 |                     -133.848 |                         0.372 |
| scidocs          | bridge_shared          |                      46.357 |                       37.890 |                         0.683 |
| scidocs          | dense_only             |                       7.089 |                        8.935 |                         0.497 |
| scidocs          | mugi_controlled        |                      41.819 |                       32.627 |                         0.651 |
| scidocs          | original               |                       0.000 |                        0.000 |                         0.000 |
| scidocs          | proposed               |                      35.410 |                       35.386 |                         0.718 |
| scidocs          | sparse_boolean_mask    |                      42.669 |                       43.147 |                         0.679 |
| scidocs          | sparse_only            |                      19.615 |                       17.291 |                         0.688 |
| scidocs          | sparse_references_only |                      40.667 |                       31.291 |                         0.591 |
| scifact          | bridge_shared          |                      30.559 |                       23.318 |                         0.697 |
| scifact          | dense_only             |                      -1.157 |                       -0.124 |                         0.463 |
| scifact          | mugi_controlled        |                      28.237 |                       20.771 |                         0.653 |
| scifact          | original               |                       0.000 |                        0.000 |                         0.000 |
| scifact          | proposed               |                      22.179 |                       20.897 |                         0.700 |
| scifact          | sparse_boolean_mask    |                      28.612 |                       25.759 |                         0.690 |
| scifact          | sparse_only            |                      19.041 |                       17.708 |                         0.677 |
| scifact          | sparse_references_only |                      26.056 |                       18.773 |                         0.640 |
| trec-covid       | bridge_shared          |                      87.445 |                       83.363 |                         0.760 |
| trec-covid       | dense_only             |                      29.819 |                       18.547 |                         0.600 |
| trec-covid       | mugi_controlled        |                      87.655 |                       83.640 |                         0.680 |
| trec-covid       | original               |                       0.000 |                        0.000 |                         0.000 |
| trec-covid       | proposed               |                      74.887 |                       66.715 |                         0.840 |
| trec-covid       | sparse_boolean_mask    |                      87.427 |                       83.338 |                         0.680 |
| trec-covid       | sparse_only            |                      71.673 |                       62.450 |                         0.740 |
| trec-covid       | sparse_references_only |                      74.941 |                       66.783 |                         0.620 |
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
| macro_equal_dataset | bridge_shared          | dense_total_reduction_pct   |    42.9656 |      16.6293 |      47.7076 |
| macro_equal_dataset | bridge_shared          | dual_depth_improvement_rate |     0.5953 |       0.5669 |       0.6232 |
| macro_equal_dataset | bridge_shared          | sparse_total_reduction_pct  |    21.2019 |      -7.5173 |      28.7308 |
| macro_equal_dataset | dense_only             | dense_total_reduction_pct   |     8.1602 |      -2.9540 |      12.1014 |
| macro_equal_dataset | dense_only             | dual_depth_improvement_rate |     0.4405 |       0.4096 |       0.4712 |
| macro_equal_dataset | dense_only             | sparse_total_reduction_pct  |     7.4888 |      -2.1804 |      11.7859 |
| macro_equal_dataset | mugi_controlled        | dense_total_reduction_pct   |    33.1075 |     -48.5820 |      41.1129 |
| macro_equal_dataset | mugi_controlled        | dual_depth_improvement_rate |     0.5452 |       0.5160 |       0.5744 |
| macro_equal_dataset | mugi_controlled        | sparse_total_reduction_pct  |    10.6119 |     -71.7058 |      21.2141 |
| macro_equal_dataset | original               | dense_total_reduction_pct   |     0.0000 |       0.0000 |       0.0000 |
| macro_equal_dataset | original               | dual_depth_improvement_rate |     0.0000 |       0.0000 |       0.0000 |
| macro_equal_dataset | original               | sparse_total_reduction_pct  |     0.0000 |       0.0000 |       0.0000 |
| macro_equal_dataset | proposed               | dense_total_reduction_pct   |    36.8965 |      18.3235 |      41.4194 |
| macro_equal_dataset | proposed               | dual_depth_improvement_rate |     0.6331 |       0.6055 |       0.6605 |
| macro_equal_dataset | proposed               | sparse_total_reduction_pct  |    36.5635 |      18.9301 |      41.3774 |
| macro_equal_dataset | sparse_boolean_mask    | dense_total_reduction_pct   |    41.1042 |      14.4916 |      45.8105 |
| macro_equal_dataset | sparse_boolean_mask    | dual_depth_improvement_rate |     0.5739 |       0.5452 |       0.6031 |
| macro_equal_dataset | sparse_boolean_mask    | sparse_total_reduction_pct  |    41.3970 |      15.0802 |      46.0176 |
| macro_equal_dataset | sparse_only            | dense_total_reduction_pct   |    28.7667 |       9.1196 |      33.1101 |
| macro_equal_dataset | sparse_only            | dual_depth_improvement_rate |     0.5951 |       0.5663 |       0.6242 |
| macro_equal_dataset | sparse_only            | sparse_total_reduction_pct  |    27.7393 |       9.2189 |      32.3753 |
| macro_equal_dataset | sparse_references_only | dense_total_reduction_pct   |    24.1704 |     -69.2579 |      33.9595 |
| macro_equal_dataset | sparse_references_only | dual_depth_improvement_rate |     0.4937 |       0.4662 |       0.5217 |
| macro_equal_dataset | sparse_references_only | sparse_total_reduction_pct  |    -0.8641 |     -95.0453 |      11.4491 |

## 主比较

| comparison                | metric       |   favorable_difference |   ci95_lower |   ci95_upper |    p_raw |   p_holm |
|:--------------------------|:-------------|-----------------------:|-------------:|-------------:|---------:|---------:|
| proposed_vs_original      | ndcg_at_10   |               0.017484 |     0.011109 |     0.023831 | 0.000100 | 0.000400 |
| proposed_vs_original      | recall_at_20 |               0.010920 |     0.006979 |     0.015136 | 0.000100 | 0.000400 |
| proposed_vs_original      | dense_depth  |            1023.550000 |   377.455419 |  2012.641552 | 0.000100 | 0.000400 |
| proposed_vs_original      | sparse_depth |             781.936102 |   356.111285 |  1339.662006 | 0.000100 | 0.000400 |
| proposed_vs_bridge_shared | ndcg_at_10   |               0.007536 |     0.003624 |     0.011564 | 0.000300 | 0.001200 |
| proposed_vs_bridge_shared | recall_at_20 |               0.002837 |    -0.000300 |     0.006139 | 0.091191 | 0.273573 |
| proposed_vs_bridge_shared | dense_depth  |            -121.429364 |  -366.994366 |    39.717006 | 0.315668 | 0.631337 |
| proposed_vs_bridge_shared | sparse_depth |             -66.450252 |  -310.622056 |    92.991215 | 0.790921 | 0.790921 |

### 结论分类

| comparison                | classification   | rule                 |
|:--------------------------|:-----------------|:---------------------|
| proposed_vs_bridge_shared | 混合               | 四项有利差值的95%区间同向，否则为混合 |
| proposed_vs_original      | 强阳性              | 四项有利差值的95%区间同向，否则为混合 |

## 公开方法完整复现

下表将各论文对应的提示词与整合规则同冻结的 Original 和 Proposed 并列展示；该表为描述性完整方法比较，预注册显著性检验仍只针对 controlled 主比较。

| source                           | method    |   ndcg_at_10 |   recall_at_20 |   dense_depth |   sparse_depth |
|:---------------------------------|:----------|-------------:|---------------:|--------------:|---------------:|
| frozen_primary_protocol          | original  |       0.4572 |         0.4586 |     1752.4284 |      1455.1354 |
| frozen_primary_protocol          | proposed  |       0.4747 |         0.4695 |      728.8784 |       673.1993 |
| published_prompt_and_integration | hyde      |       0.4114 |         0.4374 |     8588.7731 |      8080.0248 |
| published_prompt_and_integration | mugi      |       0.4584 |         0.4596 |     1396.6025 |      1393.4694 |
| published_prompt_and_integration | query2doc |       0.4728 |         0.4675 |      892.3068 |       879.2349 |

## 消融与敏感性

### 参考文本数量

|   reference_count |   ndcg_at_10 |   recall_at_20 |   dense_depth |   sparse_depth |
|------------------:|-------------:|---------------:|--------------:|---------------:|
|            1.0000 |       0.4641 |         0.4639 |     1040.8191 |       971.9339 |
|            3.0000 |       0.4730 |         0.4675 |      775.8423 |       713.2974 |
|            5.0000 |       0.4747 |         0.4695 |      728.8784 |       673.1993 |

### Sparse 算子

| method                 |   ndcg_at_10 |   recall_at_20 |   dense_depth |   sparse_depth |
|:-----------------------|-------------:|---------------:|--------------:|---------------:|
| proposed               |       0.4747 |         0.4695 |      728.8784 |       673.1993 |
| sparse_boolean_mask    |       0.4675 |         0.4660 |      626.1448 |       575.2442 |
| sparse_references_only |       0.4565 |         0.4592 |      978.5421 |       974.8536 |

### RRF 常数

|   rrf_constant |   ndcg_at_10 |   recall_at_20 |   dense_depth |   sparse_depth |
|---------------:|-------------:|---------------:|--------------:|---------------:|
|         2.0000 |       0.4791 |         0.4760 |     1088.1315 |      1015.0161 |
|        20.0000 |       0.4803 |         0.4764 |     1318.9925 |      1244.4784 |
|        60.0000 |       0.4747 |         0.4695 |      728.8784 |       673.1993 |
|       100.0000 |       0.4728 |         0.4642 |      341.8643 |       300.0350 |

### 固定 Top-L

| method        |   top_l |   ndcg_at_10 |   recall_at_20 |   complete_top20_exact_rate |
|:--------------|--------:|-------------:|---------------:|----------------------------:|
| bridge_shared |      10 |       0.4630 |         0.4511 |                      0.0000 |
| bridge_shared |      20 |       0.4633 |         0.4696 |                      0.0006 |
| bridge_shared |      50 |       0.4641 |         0.4662 |                      0.1406 |
| bridge_shared |     100 |       0.4645 |         0.4606 |                      0.4565 |
| bridge_shared |     200 |       0.4666 |         0.4647 |                      0.7287 |
| bridge_shared |     500 |       0.4670 |         0.4665 |                      0.8854 |
| bridge_shared |    1000 |       0.4671 |         0.4664 |                      0.9309 |
| original      |      10 |       0.4478 |         0.4393 |                      0.0000 |
| original      |      20 |       0.4489 |         0.4590 |                      0.0197 |
| original      |      50 |       0.4512 |         0.4577 |                      0.1382 |
| original      |     100 |       0.4553 |         0.4537 |                      0.4095 |
| original      |     200 |       0.4565 |         0.4554 |                      0.6611 |
| original      |     500 |       0.4569 |         0.4577 |                      0.8129 |
| original      |    1000 |       0.4571 |         0.4583 |                      0.8680 |
| proposed      |      10 |       0.4738 |         0.4525 |                      0.0000 |
| proposed      |      20 |       0.4727 |         0.4721 |                      0.0192 |
| proposed      |      50 |       0.4709 |         0.4697 |                      0.1654 |
| proposed      |     100 |       0.4727 |         0.4644 |                      0.4740 |
| proposed      |     200 |       0.4740 |         0.4666 |                      0.7378 |
| proposed      |     500 |       0.4743 |         0.4691 |                      0.8862 |
| proposed      |    1000 |       0.4747 |         0.4697 |                      0.9262 |

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
