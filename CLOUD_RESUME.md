# Cloud continuation — updated 2026-10-01 UTC

Read unchanged GOAL.md first: all 20 reference images plus the original opening in one real 3D world. All visual acceptance remains pending. Do not confuse functional checks, migration, source asset review or software-rendered pixels with complete GPU/visual acceptance.

## Repository state

- Working branch: development/feiting-cloud-20260930. Never write/force-push the migration branch.
- Original cloud baseline: 98486d31c6769b2a572e5d9f4a7a6754922b0e46.
- Completed migration 851f7374f1f9625c57aa1c992f4550efaa8e6bee was merged normally as a005f961390750067f68a3ee8b29e7f1a0f47056. It added historical captures/Blender sources/delivery records and changed only MIGRATION_HANDOFF.md among existing paths; active candidate unchanged.
- Sparse checkout intentionally avoids expanding all historical capture files. Do not run unbounded blob-reading commands on the full partial-clone tree merely to produce statistics.
- Active project: candidates/round40-exclusive-20260930/project. Its default still Game42c, not a claim that later candidates are rejected for all purposes. New candidates are explicitly loaded by verification tools.
- Protected cliff master remains unchanged: SHA256 abb66e414168cbd24e2495b64c27714759c844ff75582b0f71d5384d8f760dd7.

## Tools and actual rendering

Current official tools are /workspace/scratch/a29d03198654/tools-feiting/Godot_v4.5.1-stable_linux.x86_64 and tools-feiting/blender-4.5.14-linux-x64/blender, vendor-checksum verified. Earlier /workspace/shared tool paths disappeared and are obsolete. User explicitly permitted cloud Blender on September 30, overriding the previous Hub-only restriction. Do not modify either user's network settings.

Cloud desktop X11 can run Godot Compatibility, but reports Mesa llvmpipe software rendering. No hardware GPU gate is satisfied. Cloud shell does not expose the display; run graphical commands through the existing cloud desktop terminal. Use isolated XDG directories and Dummy audio. The VSync unsupported warning is known and retained, never suppress other warnings/errors.

Important Godot lifecycle fix: an off-tree Sky released before the renderer updates leaks two 349,524-byte textures. A minimal immediate-vs-settled reproduction proves this. After each instantiate, including CACHE_MODE_IGNORE reload, wait at least 3 process frames plus frame_post_draw before freeing. Wait 8 frames after cleanup. Never save the whole gameplay scene after adding it to the live tree merely to avoid this error, since ready changes state.

## Candidates and evidence

### 42d — persistent rain/snow instance fix

Commit e6d6cb37597b2eb596649da6f2ca03675d0d3fb7. Scene SHA256 5742de44e7f44070ca7475e801ea82b4f9be6433b8a1cef55e00aa667f1607e9.

42b/42c had no saved rain/snow buffers. 42d explicitly allocates/copies and reconstructs the exact original seeded payload and placement. 100 allocation checks pass. All 48,000 buffer floats survive reload. Native scene geometry/collision/structure of 10,446 other nodes is equivalent; 1,524 null shader parameters were explicitly serialized as their declared defaults.

Initial build run stays failed because it emitted the Sky cleanup errors. Do not rewrite it as passed. Separate delayed reload and actual-tree smoke recover this exact saved scene without rebuilding. Smoke: 17/17 checks, 12 raw images, exit 0, no texture leak, software renderer. Rain/snow move and are visible but far too sparse for storm/blizzard reference fidelity. 1341 initial differential was contaminated by lightning settling; use the explicit off/restored independent report instead. Details: cloud-evidence/multimesh42d-diagnosis-20260930-1914/recovery-report.json.

### 43 — upper-cloud volume comparison

Commit abafd821dd58c09c44506997ae317deb76ccd846. Scene SHA256 a3a741df4fb4f19bd397e26050cd4854bb9e5b6d4344d8af0dbf1bc45322dc95.

Replaces only 12 upper-cloud groups with retained upper43 editable source. Build/reload preservation passed without ERROR. Focused 54 checks/26 actual software-rendered images passed; all visual acceptance pending. CPU source preview has real rounded undersides, but actual night views still read as rock/ball clusters. Cloud-sea floor still has coarse rock-like facets. Diag-only hiding of DistantCloudBank41 removes the original large opening-view gray ceiling, confirming exact source; these hidden-group images are not production beauty evidence.

### 44 — distant-cloud bank geometry

Saved scene SHA256 e679ad1510b8e222b83194534f58752a6f40edc8eb0e1c4a128c042af1feb347. Build/reload preservation passed. Focused software-renderer run completed 117 limited checks and 32 images with exit 0 and no ERROR, retaining the known VSync warning. Independent visual review rejects it as a finished match. Check /workspace/shared/feiting44-last-run.txt for exact evidence.

New editable source-assets/cloud-bank44 retains three variants, each 21 closed pieces/2,400 triangles. Only the 56 original distant bank meshes were replaced; original names, transforms and variation mapping preserved. Opening 1343 and 1128 frontal sky opens substantially. This does not mean all gray ceiling is gone: side/back retain thick gray clouds, and high-altitude perimeter can be too sparse. Independent review is cloud-evidence/cloud44-independent-review.md when complete. The 1128 translated camera enters terrain; preserve that failed observation, do not count it as valid flight evidence.

### 45 — material-only paired comparison completed

Scene SHA256 465b305290637792c09a8750d3c7d66bc63fbf0e904dc7f14ff75e86054a3159. Only diffuse_mode on 9 copied native cloud materials / 1,808 surfaces changes to Lambert Wrap. Full world and every other material property passed save/reload preservation. Latest run material45-20260930T205730Z-KXhKIP completed 13 images of44 and13 of45 with matched poses/time, no ERROR, known VSync warning only. Material/render checks pass; original1128 350m path is blocked and retained, separately verified150m path is supplemental camera evidence only. Complete flight and hardware GPU acceptance remain false.

Independent parent review actually examined1343 and1216-side two pairs: dark hard edges and black spots are softened; retain as a material candidate for comparison on46, not final acceptance. White clipping, repeated rocky silhouettes and geometry gaps remain.1128/1342 were not included in that independent review.

Earlier failed runs remain intact. Completely unmodified repeated fingerprints drifted due Godot4.5.1 var_to_bytes(NodePath) uninitialized alignment padding. Byte dumps prove all path/content semantics identical. Canonical form now retains a NodePath type tag + exact path text, recursively sorts dictionary keys, and retains mesh/MM bytes and all content.12 independent processes /24 repeated comparisons, content-change sensitivity and path round-trips pass. This is an audit fix, not permission to omit PackedScene resources.

### 46 — cloud-sea native source integrated and visually rejected

Independent editable source-assets/cloud-sea46/cloud_sea46.blend and three project/assets/clouds46 GLBs are prepared, with original lobe controls retained and 15 CPU asset views. Three closed single-mesh volumes replace the old disconnected slab/crown pieces; source41 and protected cliff hashes unchanged. Actual Game44 back-view diagnostic run sea46-back-diagnosis-20260930T204051Z-qQSJnj completed 5 images (including boot) and exit 0. Both 1343 and 1128 back ceilings disappear when only CloudSea is temporarily hidden, confirming source responsibility. This diagnostic is never production visual acceptance. A 46 integration builder uses Game44 as base, independent of45. Second build passed after the NodePath audit fix, saving SHA256 2b16ce757de6368a600cd5ee53741aa422e3ba8c5f717b0139da0f856910d5d7; focused graphical verification completed in cloudsea46-20260930T210603Z-nd2yLv with100 limited checks and15 images, build/verify/wrapper exit0.1216 views still have large rock-like dark masses and gaps; back-view ceilings remain, so visual review rejects it.47 material merge started in material47-20260930T211818Z-pG3XFd after checking no prior run existed; check terminal reports before resuming, never duplicate that job. Preserve all 25 original CloudSea node names/transforms and derive variant mapping from actual old resource names. New asset undersides may still look too continuous and smaller footprint may create gaps; runtime images must judge it.

## Publication boundary

Cloud has public repository read but lacks Git shell write authentication. No token was copied or requested. A verified incremental git bundle can be materialized through authorized Library transfer into the existing authenticated migration executor only to import and normally push the independent cloud branch; this does not resume local development. Remote publication must be read back before claiming push success. Tool binaries, personal configuration, credentials and signed upload URLs stay excluded.

A complete-reference survey tool is prepared at project/tools/survey_reference_views.gd (4.5.1 parse passed with isolated XDG directories), wrapper /workspace/shared/a.sh. It records original boot identity plus exact20 GOAL IDs, optional side/back, collision checks and same-world IDs; it never replaces scenery or claims hardware/visual acceptance. It has not yet run.

## Checkpoint 2026-09-30 23:13 UTC

Game47 material merge finished: SHA256 ba236fdb78f662351ad8e89d82df4642b27721638412c833f86f6e8f682caa32, 104193781 bytes; 1333 surfaces/9 materials. material47-20260930T211818Z-pG3XFd completed13 matched46/47 pairs; build/baseline/candidate exit0. Independent review game47-independent-review.md rejects visual completion. Full survey now completed in full-reference-survey-20260930T225223Z-Tc88Sk:61PNG,169 limitedchecks,exit0. Developer all-view review full-survey47-review.md records every front/side/back gap; all21 scenes still visuallyfailed, hardwareGPU and fullflight unmet. No Godot47 jobs pending.

45–47 screenshots/reports successfully shared to authorized Slack thread as104PNG package, files F0C5CG1MZC7/F0C5MLXH0E7/F0C5TP2A7SN. Do not duplicate. Original e6d6cb3 ZIP split losslessly into Library20MiB+13.97MB parts, IDs libfile_00099c21482c8191922a93ae0a771006 and libfile_c42968c270648191830c8bd725179e41; manifest libfile_0d54bb1f243c8191aad1e545e7c279ad. Parent handles manual desktop download/push; later commits remain local.

Lake48 in progress in source-assets/lake48 and project/assets/lake48. Do not launch duplicate builds. Actual renderer export lake48-export-20260930T231109Z-JakGxl exit0 provides500 real nonzero scatter transforms in base47.json; independent headless support-only export must not overwrite these. Worker sculpt_shared_lake_basin48 owns source/builder preparation; parent task owns GUI. Preserve complete failed inputs and quantify every affected instance.

## Checkpoint 23:24 UTC: tool-path recovery and Lake48

Shared directory disappeared around23:18; cause unestablished. No project data lost. Matched official tools were re-downloaded with vendor checksums to /workspace/scratch/a29d03198654/tools-feiting. Godot4.5.1f62fdbde1 and Blender4.5.14 versions verified. Use its userdata/{cache,data,config}. Old /workspace/shared paths are obsolete. Shell/tmp and GUI/tmp do not share files; run project/scratch scripts through actual terminal27262979. New entry /workspace/scratch/a29d03198654/l48.sh, durable source source-assets/lake48/launch_lake48.sh; latest-run pointer tools-feiting/feiting48-last.txt.

Lake48 first build lake48-20260930T231655Z-ieSp4X failed on PackedScene raw bundle fingerprint before Game48 was written. Three partial native assets archived with SHA under failed-native. Read-only diagnostic proves names/nodes/node_paths packing tables reorder on serialization but variants/connections/version and all5instantiated nodes' stored content remain equal. Fixed prefab verification uses complete instantiated properties/resources/order/owner/groups/connections/editable instances and nonbundle properties; ordinary meshes/shapes/MM retain exact comparison. Matching4.5.1 parse passed. Second build lake48-20260930T232337Z-Qm1Vgm currently running; check exit/status before launching anything again.

Actual lake source4meshes prepared, 500scatter retained:206unchanged/104verticalsupport/190relocated. Real renderer base export remains lake48-export-20260930T231109Z-JakGxl. Upper mountain sources unchanged and11mountains included in support queries. These values are source checks pending actual saved48 GUI verification. Original20+opening still notaccepted.

Game47 and full survey committed8ace18527c3c1264f33906b3dfd9b27c6f86d595, timing clarification574dd42. Full61images+report sent Slack F0C5S25PKM4. Separate Slack clarification explains survey0.35s is between lightning flashes, so absence in stills is not a failed functional lightning test. Development remains local awaiting existing manual bundle bridge. Both original e6ZIP lossless parts persist in feiting-parts-library-20260930T2039 and Library despite loss of shared original transfer folder.

## Latest checkpoint 2026-10-01 00:30 UTC

49 completed, not accepted: SHA52d13fcb7ea412d3a0fae2eedb1d0f9c369dbe06c0da320d786c26c97c475ec8. Source native commitd66f8bf, runtime/evidence265c2dc. Four islands/rock,199meshes,8086tris,7pines added with closed roots andactual support. Runlake49-20260930T234925Z-pYs5Nx build0/verifier0,894boundedchecks,42PNG(13baseline48+29candidate49). All29candidate images reviewed, clear cyan projected root artifacts rejected. Required350m paths inheritedblocked; no new protected150/200m obstruction. Firstlaunch234519failed beforeGodot;firstactual234621group-scope failure retained348nativefiles. ./path normalization fixed new496keys only;0oldgroup changes plusintentionaloldgroup mutation negativecontrol. Source-manifest-diagnostic-correction.json preserves old manifest and identifies onlyupdatedCPU render script/front image provenance.

49 Slack fulfilled successfully WITHOUT repeatedPOST despite lost curlpoll handles: F0C5U3RPT2N game49-lake-islands-water-failure.png and F0C5W6JM80Z game49-islands-and-water-diagnostics.zip(117PNG,39MB). Both complete callsserverconfirmedbytes. Do not resend. cloud-delivery/lake49-20261001/upload-state.json recordsfinalstatus.

Actual root cyan issue established: Ocean screen-ray hitY misused asverticaldepthatwaterXZ. Real forestonepoint23.24m depthwascoloredas2.317m fromroot15m awayXZ;leftisland23.68vs3.296m with41mshift. Native rootsmustremainclosed/bed-supported,notraisedtohide.

Read-only depth causal test FINISHED: depth50-control-v2-20261001T002033Z-OAubiw exit0/noERROR,6PNG.1128/1129 Aoriginal→Bonlyrealworldsigned-heightdepth→A2restore. IndependentA/A2fullimage differences0each;A/B31682/19633pixels,upper300rows0. Candidate49SHAunchanged,originalshaderrestored. ConfirmedcyanbandsremovedinB.1mgridfrom55actualmeshes/71820tris;1,181,953gridpointsnoholes,butcontinuoussteepcoasterror6.86m and0-lineP95.72m/max1.91m remain;notfinalshoreacceptance. Four0.25m localpatchesnowbeingpreparedbyworker. Slack diagnosticdeliveredF0C5P38JGDB imageandF0C5SDJ5ZRC6imageZIP;do notduplicate.

50 reflection NOT yet built. Primitive sameWorld3D mirroredcamera proof in cloud-evidence/reflection50-prototype,commit6bb5d89. Failedsubmergedyellowbox contaminationretained;reflection-onlyCAMERA_VISIBLE_LAYERSbit19/worldYclipremoves70610yellowpx;exactsame-shadercontroltop3000changed. Prototypeonly,notgamebeauty.

Official material conversion templates now4groups, generated via actualGodot4.5.1InspectorMaterialpropertyConvert toShaderMaterialandSaveinsavedholderresources. source-assets/reflection50/official-native-conversions contains4self-containedshader.tres/.gdshader,manifests,fullconversion-projectprovenance. Group1double-sidedvertexcolorBurleyrough1,group2CullBackvertexcolorLambertrough.96,group3unshadedtransparentrainbow,group4actualnativeemissionlantern. Neverapproximateunknownfeatures. NativeMaterial_get_shader_ridnotpublic4.5.1;do notinventbinding. Staticnegative-Ytemplateswerenotenough:ready49bindings5530→5581,569switches;runtimeauthorityparentsurface_materialmatters. WorkerhasruntimeauditfullMesh/MM/camera/lightmasks;Rain/Snowvisibility0in晴态mustnotexclude dynamicrange. AllVisualsavedlayers1,bit18water/19markerpotentialreservedbutrecheckmasks.

GUI IMPORTANT: Originalterminal27262979currentlyoccupiedbyofficialmaterial-converter50editor39845891. Itsclosewasdeniedtwice;do notclose/kill/restartorloseitsstate. All4holderresults saved/extracted,butglobaldirtymarkpersists. KepteditoropenandusednormalLoadResource+ConvertUIwithoutdiscardingstate. New飞艇testterminal27267931isoursandidleafterdepthdiag;MAZterminal27263811donottouch. CurrentCUAbindingsconverter/testTerminalmaypersist. Nativeappcoordinateclickswereunreliable;documentedcua.computer.get_screenshot/clickglobalcoordinatesworks. Alwaysfreshdesktopshotbeforecoords. Activeeditorcanremainbackgroundduringgraphicaltests;nohardwareperfclaims.

Nextworker sculpt_shared_lake_basin48 owns ongoinglake50plan/bindings/depthpatches andits integrate_native_islands49worker;allnewworkercreationcurrentlythreadlimit. Need all50materialauthoritychanges/scopesexplicit,strictnativefeaturetemplate matching,mainpassbefore/afterwithreflection/depth/clipdisabledcontrol,refpassunderwaterclip/rotation/motion/occlusionvalidation,geographiclakeblend(noReferenceIDscenery),nativepersistentSubViewport/Camera sameWorld3D. ParenttaskrunsGUIonly. NoGodotgamejobcurrentlyrunning;editoronly.

## Latest routing/user delivery 2026-10-01 00:51 UTC

User explicitly requested separate newSlack channels with progress/currentappearance. ParentcreatedandIverifiedprivate #feiting-progress C0C5WDC9649,owneruserUKQMWM9MZjoined. All future FeiTing progress goes to this new channel, NOT the old self-DM thread. Current channel summary https://tupworld.slack.com/archives/C0C5WDC9649/p1790815652390219 . Five Game49 realPNG sharedsuccessfullyinthatsummarythread: openingF0C5SHD38F8,lakeF0C5WEB3FC1,islandbackF0C6NSUJK40,nightcloudsF0C5UBSE4D8,cabinF0C5UBTD5H8. No researchframe substitutedforcurrentversion. Allcaptionedcloudcandidate/softwarerender/notaccepted;summaryhasprogress/failures/Gitwriteblock. Do notduplicate delivery. Latest freshGame49overviewrun current49-overview-20261001T004646Z-qrMDCR completedexit0,boot+1216+1278 actualsavedworld,source/defaultunchanged;committedb6168a1. NoGodotgameprocessleftfromthisrun.

Workplan split: Game50 is now water-depth-only persistentfix using1m+four0.25m patches, Oceancopy+externaltextures/controlleronly. SameWorlddynamicreflection/114materialclip planretainedforindependent51. At00:44:53UTCworkerhadwrittenproject/scripts/lake_depth50.gd andproject/assets/lake_depth50/lake_water_depth50.gdshader, matching4.5.1parsepass;source-assets/lake_depth50/shader-change-ledger.jsonverifiesremovingtwoinsertsrestores49shaderexactincludingCRLF. Builder/verifierstillbeingcompleted;do notclaimGame50built. ParentaskedactualmodelID;visibletool/runtimeprovidesnone,soAstraisnotverified. Do notguessmodelname. Explicitusercontinuationstillactive.

## Latest checkpoint 2026-10-01 01:29 UTC

Game50 depth-only build/reload and corrected independent verifier completed successfully. Candidate SHA031b39ea75680e98fbed4882507251ec0ebfb3469300f82402891a0137351ff0. Local commitc1e78a4. Successful run cloud-evidence/depth50-verify-v2-20261001T010738Z-G3enLm:227 bounded checks,60actual PNG,12 poses, all required original49/disabled50/restored controls fullRGBA zero-difference; independent PNG recomputation agrees. All2235PhysicsObject modes/layers/masks/RIDs unchanged by freeze. Original350m camera routes still blocked,150m/200m remain clear, no full-airship claim. All12 enabled images reviewed by developer; large cyan root columns removed but thin cyan edges, strong waves, no mirror reflections and major scene/reference gaps remain. Hardware/visual/total acceptance false. Detailed report cloud-evidence/depth50-review.md.

First50 verifier preserved in depth50-20261001T005643Z-gxCMO5 with27frames: process_mode disabling removed collision objects and global-uniform getter produced errors; manually interrupted, no fabricated exit code. Correctedv2 stops callbacks only. Do not reuse invalid first motion outcomes.

NewSlack channel delivery succeeded: https://tupworld.slack.com/archives/C0C5WDC9649/p1790817346914309 . Two current50images F0C5NE8J7JP/F0C5SN635P0 plus31.32MB87frame(success+failed)report ZIP F0C5PC0AQSZ, allHTTP200 andcompleteconfirmed. Trackingcloud-delivery/depth50-20261001/delivery-manifest.json. No duplicate sharing. CloudGitwriteblock/manualtransfer remains; later commits stilllocal.

51 prepared actualcontroller/watershader/materialfactory;114scopedmaterials(73Shader/41Standard),4officialnative templates,12custom/generatedshader bodies. Exact reversiblecodeinjection, olduniforms/flags retained, next_pass114allnull and nonnullrejected. Primitive true-render compile/control finishedexit0 inreflection51-source-compile-20261001T011358Z-XFxZBJ;original/injectedmainpassallRGBA0difference, markerclips4894pixels, diagnosticboxesonly. Committed1563764. Purecameraopticsunit1715points/120cases passedmaxNDC3.42e-5 after correctingtester'schildviewportaspect, retainedfailedtests, commitf391d84. Neitherisfullsceneacceptance.

01:29UTCstartedbuilder-only51 diagnosticOFF via source-assets/reflection51/build_diagnostic51.sh, pointertools-feiting/feiting51-build-last.txt. Checkactualexitbeforeanyrepeat. Controllerclip/reflectiondefaultfalse; thissaveddiagnosticcandidatewillNOTshowreflectiononordinarylaunch. Workercontinuesfullmainpass/clip/reflectionverifier. Afteractualgates,authoraseparateexplicitdefaultONcandidateandreteststartup;donotoverwriteoffdraft. GUItestTerminal27267931isoccupiedbycurrentbuilder;retainedconvertereditor39845891mustremainuntouched. Existingworldnative49/50/default42c/protectedcliffhashunchanged. LatestmodelIDstillnotexposed;Astraunverified.
