# West53有限原生集成实测结果

保存候选：`res://scenes/candidate53d-west/Game53dWest.tscn`，SHA256`6ec57b72a831d6fa906a8d866c339909de55c9c42297a038dcd429b18d0c2b18`。成功build/reload证据`cloud-evidence/rim53d-west-build-20261001T063353Z-eEO0XE`；fresh v2证据`cloud-evidence/rim53d-west-verify-v2-20261001T064631Z-OrTCQY`。

202项检查通过、无失败，10张实际PNG均已逐张查看。实际山体/建筑支承和ground_height最大误差0.000488m；1261个运行缓存索引精确，120个更新、1141个未变；散布支承最大误差0.000610m，位置最大误差0.00000573m。原340三角根ArrayMesh精确保留；仅4个新增mesh、west碰撞faces和120个MM平移槽改变；248原绑定、114材质、48000天气float和非目标图保持。

两个原视角的150m横移和200m前进均保持通过。350m横移仍失败：1128safe_fraction0.9931640625，1129safe_fraction0.55859375，均命中原Ground_1_-2；未豁免。1344原两像素转换门、完整物理飞艇飞行、未来stream及硬件GPU仍未通过/未验证。实际渲染器为llvmpipe软件Compatibility，不能改称硬件GPU通过。

第一fresh verifier的失败完整保留。原因是4条北建筑缓冲射线的expected来自只含六tile的离线子集，漏了Ground_1_-4。独立完整51b实际171条射线证明所有受保护点与候选真实高度差≤0.488mm。v2保留全部171检查和3cm阈值，固定独立报告SHA，未改资源或候选。详见`verification-v2/README.md`及`baseline-candidate-171-comparison.json`。

## 视觉结论

只保留为west单山有限集成，不是参考通过。1128主峰入框、雪沟方向改善，1129左山层次更完整；但全湖仍以绿岸为主，中远山的尖锥和空面明显，船极小且近正面，旧球状云团过大。侧/背视图保留大量原草坡和云块。1275码头附近巨型简单斜面与悬空感、1276粗锥群仍明显失败。原状保留不等于视觉验收。

下一步仅准备cirque的独立原生详细形体方案，使用本候选为新基底，冻结west成果及其已验证资源；不把其他三座旧失败首稿并入。
