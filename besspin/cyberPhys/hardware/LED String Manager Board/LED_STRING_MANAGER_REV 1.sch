<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE eagle SYSTEM "eagle.dtd">
<eagle version="9.6.2">
<drawing>
<settings>
<setting alwaysvectorfont="yes"/>
<setting verticaltext="up"/>
</settings>
<grid distance="0.05" unitdist="inch" unit="inch" style="dots" multiple="1" display="yes" altdistance="0.01" altunitdist="inch" altunit="inch"/>
<layers>
<layer number="1" name="Top" color="4" fill="1" visible="no" active="no"/>
<layer number="2" name="Route2" color="1" fill="3" visible="no" active="no"/>
<layer number="3" name="Route3" color="4" fill="3" visible="no" active="no"/>
<layer number="4" name="Route4" color="1" fill="4" visible="no" active="no"/>
<layer number="5" name="Route5" color="4" fill="4" visible="no" active="no"/>
<layer number="6" name="Route6" color="1" fill="8" visible="no" active="no"/>
<layer number="7" name="Route7" color="4" fill="8" visible="no" active="no"/>
<layer number="8" name="Route8" color="1" fill="2" visible="no" active="no"/>
<layer number="9" name="Route9" color="4" fill="2" visible="no" active="no"/>
<layer number="10" name="Route10" color="1" fill="7" visible="no" active="no"/>
<layer number="11" name="Route11" color="4" fill="7" visible="no" active="no"/>
<layer number="12" name="Route12" color="1" fill="5" visible="no" active="no"/>
<layer number="13" name="Route13" color="4" fill="5" visible="no" active="no"/>
<layer number="14" name="Route14" color="1" fill="6" visible="no" active="no"/>
<layer number="15" name="Route15" color="4" fill="6" visible="no" active="no"/>
<layer number="16" name="Bottom" color="1" fill="1" visible="no" active="no"/>
<layer number="17" name="Pads" color="2" fill="1" visible="no" active="no"/>
<layer number="18" name="Vias" color="2" fill="1" visible="no" active="no"/>
<layer number="19" name="Unrouted" color="6" fill="1" visible="no" active="no"/>
<layer number="20" name="Dimension" color="15" fill="1" visible="no" active="no"/>
<layer number="21" name="tPlace" color="7" fill="1" visible="no" active="no"/>
<layer number="22" name="bPlace" color="7" fill="1" visible="no" active="no"/>
<layer number="23" name="tOrigins" color="15" fill="1" visible="no" active="no"/>
<layer number="24" name="bOrigins" color="15" fill="1" visible="no" active="no"/>
<layer number="25" name="tNames" color="7" fill="1" visible="no" active="no"/>
<layer number="26" name="bNames" color="7" fill="1" visible="no" active="no"/>
<layer number="27" name="tValues" color="7" fill="1" visible="no" active="no"/>
<layer number="28" name="bValues" color="7" fill="1" visible="no" active="no"/>
<layer number="29" name="tStop" color="7" fill="3" visible="no" active="no"/>
<layer number="30" name="bStop" color="7" fill="6" visible="no" active="no"/>
<layer number="31" name="tCream" color="7" fill="4" visible="no" active="no"/>
<layer number="32" name="bCream" color="7" fill="5" visible="no" active="no"/>
<layer number="33" name="tFinish" color="6" fill="3" visible="no" active="no"/>
<layer number="34" name="bFinish" color="6" fill="6" visible="no" active="no"/>
<layer number="35" name="tGlue" color="7" fill="4" visible="no" active="no"/>
<layer number="36" name="bGlue" color="7" fill="5" visible="no" active="no"/>
<layer number="37" name="tTest" color="7" fill="1" visible="no" active="no"/>
<layer number="38" name="bTest" color="7" fill="1" visible="no" active="no"/>
<layer number="39" name="tKeepout" color="4" fill="11" visible="no" active="no"/>
<layer number="40" name="bKeepout" color="1" fill="11" visible="no" active="no"/>
<layer number="41" name="tRestrict" color="4" fill="10" visible="no" active="no"/>
<layer number="42" name="bRestrict" color="1" fill="10" visible="no" active="no"/>
<layer number="43" name="vRestrict" color="2" fill="10" visible="no" active="no"/>
<layer number="44" name="Drills" color="7" fill="1" visible="no" active="no"/>
<layer number="45" name="Holes" color="7" fill="1" visible="no" active="no"/>
<layer number="46" name="Milling" color="3" fill="1" visible="no" active="no"/>
<layer number="47" name="Measures" color="7" fill="1" visible="no" active="no"/>
<layer number="48" name="Document" color="7" fill="1" visible="no" active="no"/>
<layer number="49" name="Reference" color="7" fill="1" visible="no" active="no"/>
<layer number="51" name="tDocu" color="7" fill="1" visible="no" active="no"/>
<layer number="52" name="bDocu" color="7" fill="1" visible="no" active="no"/>
<layer number="88" name="SimResults" color="9" fill="1" visible="yes" active="yes"/>
<layer number="89" name="SimProbes" color="9" fill="1" visible="yes" active="yes"/>
<layer number="90" name="Modules" color="5" fill="1" visible="yes" active="yes"/>
<layer number="91" name="Nets" color="2" fill="1" visible="yes" active="yes"/>
<layer number="92" name="Busses" color="1" fill="1" visible="yes" active="yes"/>
<layer number="93" name="Pins" color="2" fill="1" visible="no" active="yes"/>
<layer number="94" name="Symbols" color="4" fill="1" visible="yes" active="yes"/>
<layer number="95" name="Names" color="7" fill="1" visible="yes" active="yes"/>
<layer number="96" name="Values" color="7" fill="1" visible="yes" active="yes"/>
<layer number="97" name="Info" color="7" fill="1" visible="yes" active="yes"/>
<layer number="98" name="Guide" color="6" fill="1" visible="yes" active="yes"/>
<layer number="99" name="SpiceOrder" color="5" fill="1" visible="yes" active="yes"/>
<layer number="200" name="200bmp" color="1" fill="10" visible="yes" active="yes"/>
<layer number="201" name="201bmp" color="2" fill="10" visible="yes" active="yes"/>
<layer number="202" name="galois_bars" color="14" fill="1" visible="yes" active="yes"/>
</layers>
<schematic xreflabel="%F%N/%S.%C%R" xrefpart="/%S.%C%R">
<libraries>
<library name="frames" urn="urn:adsk.eagle:library:229">
<description>&lt;b&gt;Frames for Sheet and Layout&lt;/b&gt;</description>
<packages>
</packages>
<symbols>
<symbol name="FRAME_A_L" urn="urn:adsk.eagle:symbol:13882/1" library_version="1">
<frame x1="0" y1="0" x2="279.4" y2="215.9" columns="6" rows="5" layer="94" border-bottom="no"/>
</symbol>
<symbol name="DOCFIELD" urn="urn:adsk.eagle:symbol:13864/1" library_version="1">
<wire x1="0" y1="0" x2="71.12" y2="0" width="0.1016" layer="94"/>
<wire x1="101.6" y1="15.24" x2="87.63" y2="15.24" width="0.1016" layer="94"/>
<wire x1="0" y1="0" x2="0" y2="5.08" width="0.1016" layer="94"/>
<wire x1="0" y1="5.08" x2="71.12" y2="5.08" width="0.1016" layer="94"/>
<wire x1="0" y1="5.08" x2="0" y2="15.24" width="0.1016" layer="94"/>
<wire x1="101.6" y1="15.24" x2="101.6" y2="5.08" width="0.1016" layer="94"/>
<wire x1="71.12" y1="5.08" x2="71.12" y2="0" width="0.1016" layer="94"/>
<wire x1="71.12" y1="5.08" x2="87.63" y2="5.08" width="0.1016" layer="94"/>
<wire x1="71.12" y1="0" x2="101.6" y2="0" width="0.1016" layer="94"/>
<wire x1="87.63" y1="15.24" x2="87.63" y2="5.08" width="0.1016" layer="94"/>
<wire x1="87.63" y1="15.24" x2="0" y2="15.24" width="0.1016" layer="94"/>
<wire x1="87.63" y1="5.08" x2="101.6" y2="5.08" width="0.1016" layer="94"/>
<wire x1="101.6" y1="5.08" x2="101.6" y2="0" width="0.1016" layer="94"/>
<wire x1="0" y1="15.24" x2="0" y2="22.86" width="0.1016" layer="94"/>
<wire x1="101.6" y1="35.56" x2="0" y2="35.56" width="0.1016" layer="94"/>
<wire x1="101.6" y1="35.56" x2="101.6" y2="22.86" width="0.1016" layer="94"/>
<wire x1="0" y1="22.86" x2="101.6" y2="22.86" width="0.1016" layer="94"/>
<wire x1="0" y1="22.86" x2="0" y2="35.56" width="0.1016" layer="94"/>
<wire x1="101.6" y1="22.86" x2="101.6" y2="15.24" width="0.1016" layer="94"/>
<text x="1.27" y="1.27" size="2.54" layer="94">Date:</text>
<text x="12.7" y="1.27" size="2.54" layer="94">&gt;LAST_DATE_TIME</text>
<text x="72.39" y="1.27" size="2.54" layer="94">Sheet:</text>
<text x="86.36" y="1.27" size="2.54" layer="94">&gt;SHEET</text>
<text x="88.9" y="11.43" size="2.54" layer="94">REV:</text>
<text x="1.27" y="19.05" size="2.54" layer="94">TITLE:</text>
<text x="1.27" y="11.43" size="2.54" layer="94">Document Number:</text>
<text x="17.78" y="19.05" size="2.54" layer="94">&gt;DRAWING_NAME</text>
</symbol>
</symbols>
<devicesets>
<deviceset name="FRAME_A_L" urn="urn:adsk.eagle:component:13939/1" prefix="FRAME" uservalue="yes" library_version="1">
<description>&lt;b&gt;FRAME&lt;/b&gt; A Size , 8 1/2 x 11 INCH, Landscape&lt;p&gt;</description>
<gates>
<gate name="G$1" symbol="FRAME_A_L" x="0" y="0" addlevel="always"/>
<gate name="G$2" symbol="DOCFIELD" x="172.72" y="0" addlevel="always"/>
</gates>
<devices>
<device name="">
<technologies>
<technology name=""/>
</technologies>
</device>
</devices>
</deviceset>
</devicesets>
</library>
<library name="USER_DOC FRAMES">
<packages>
</packages>
<symbols>
<symbol name="TITLE_BLOCK_GALOIS">
<wire x1="0" y1="0" x2="106.68" y2="0" width="0.254" layer="94"/>
<wire x1="106.68" y1="0" x2="106.68" y2="16.51" width="0.254" layer="94"/>
<wire x1="106.68" y1="16.51" x2="106.68" y2="24.13" width="0.254" layer="94"/>
<wire x1="106.68" y1="24.13" x2="106.68" y2="31.75" width="0.254" layer="94"/>
<wire x1="106.68" y1="31.75" x2="88.9" y2="31.75" width="0.254" layer="94"/>
<wire x1="88.9" y1="31.75" x2="62.23" y2="31.75" width="0.254" layer="94"/>
<wire x1="62.23" y1="31.75" x2="0" y2="31.75" width="0.254" layer="94"/>
<wire x1="0" y1="31.75" x2="0" y2="24.13" width="0.254" layer="94"/>
<text x="2.54" y="25.4" size="2.54" layer="94" font="vector">&gt;DOC_NAME</text>
<text x="64.77" y="25.4" size="2.54" layer="94" font="vector">&gt;DOC_NUMBER</text>
<text x="91.44" y="25.4" size="2.54" layer="94" font="vector">&gt;DOC_REVISION</text>
<text x="2.54" y="17.78" size="2.54" layer="94" font="vector">&gt;INITIALS_DRAWN</text>
<text x="17.78" y="17.78" size="2.54" layer="94" font="vector">&gt;INITIALS_CHECKED</text>
<text x="91.44" y="17.78" size="2.54" layer="94" font="vector">&gt;SHEET</text>
<text x="1.27" y="29.21" size="1.27" layer="94" font="vector">DOC TITLE</text>
<wire x1="0" y1="24.13" x2="0" y2="16.51" width="0.254" layer="94"/>
<wire x1="0" y1="16.51" x2="0" y2="0" width="0.254" layer="94"/>
<wire x1="0" y1="24.13" x2="15.24" y2="24.13" width="0.254" layer="94"/>
<wire x1="15.24" y1="24.13" x2="30.48" y2="24.13" width="0.254" layer="94"/>
<wire x1="30.48" y1="24.13" x2="62.23" y2="24.13" width="0.254" layer="94"/>
<wire x1="62.23" y1="24.13" x2="62.23" y2="31.75" width="0.254" layer="94"/>
<text x="63.5" y="29.21" size="1.27" layer="94" font="vector">DOC NUMBER</text>
<wire x1="62.23" y1="24.13" x2="88.9" y2="24.13" width="0.254" layer="94"/>
<wire x1="88.9" y1="24.13" x2="88.9" y2="31.75" width="0.254" layer="94"/>
<text x="90.17" y="29.21" size="1.27" layer="94" font="vector">DOC REVISION</text>
<wire x1="88.9" y1="24.13" x2="106.68" y2="24.13" width="0.254" layer="94"/>
<text x="3.81" y="21.59" size="1.27" layer="94" font="vector">DRAWN BY</text>
<text x="19.05" y="21.59" size="1.27" layer="94" font="vector">CHECKED BY</text>
<wire x1="0" y1="16.51" x2="15.24" y2="16.51" width="0.254" layer="94"/>
<wire x1="15.24" y1="16.51" x2="15.24" y2="24.13" width="0.254" layer="94"/>
<wire x1="15.24" y1="16.51" x2="30.48" y2="16.51" width="0.254" layer="94"/>
<wire x1="30.48" y1="16.51" x2="30.48" y2="24.13" width="0.254" layer="94"/>
<text x="33.02" y="17.78" size="2.54" layer="94" font="vector">&gt;LAST_DATE_TIME</text>
<text x="31.75" y="21.59" size="1.27" layer="94" font="vector">LAST SAVED</text>
<wire x1="30.48" y1="16.51" x2="88.9" y2="16.51" width="0.254" layer="94"/>
<text x="90.17" y="21.59" size="1.27" layer="94" font="vector">SHEET</text>
<wire x1="88.9" y1="16.51" x2="106.68" y2="16.51" width="0.254" layer="94"/>
<wire x1="88.9" y1="24.13" x2="88.9" y2="16.51" width="0.254" layer="94"/>
<rectangle x1="35.3949" y1="1.5875" x2="35.9283" y2="1.6637" layer="200"/>
<rectangle x1="34.7853" y1="1.6637" x2="36.5379" y2="1.7399" layer="200"/>
<rectangle x1="34.4043" y1="1.7399" x2="36.8427" y2="1.8161" layer="200"/>
<rectangle x1="34.1757" y1="1.8161" x2="37.0713" y2="1.8923" layer="200"/>
<rectangle x1="34.0233" y1="1.8923" x2="37.2999" y2="1.9685" layer="200"/>
<rectangle x1="33.8709" y1="1.9685" x2="37.5285" y2="2.0447" layer="200"/>
<rectangle x1="33.7185" y1="2.0447" x2="37.6809" y2="2.1209" layer="200"/>
<rectangle x1="33.5661" y1="2.1209" x2="37.8333" y2="2.1971" layer="200"/>
<rectangle x1="33.4899" y1="2.1971" x2="37.9857" y2="2.2733" layer="200"/>
<rectangle x1="33.4137" y1="2.2733" x2="38.1381" y2="2.3495" layer="200"/>
<rectangle x1="33.3375" y1="2.3495" x2="35.2425" y2="2.4257" layer="200"/>
<rectangle x1="36.3855" y1="2.3495" x2="38.2143" y2="2.4257" layer="200"/>
<rectangle x1="33.2613" y1="2.4257" x2="34.9377" y2="2.5019" layer="200"/>
<rectangle x1="36.6903" y1="2.4257" x2="38.3667" y2="2.5019" layer="200"/>
<rectangle x1="33.1851" y1="2.5019" x2="34.7853" y2="2.5781" layer="200"/>
<rectangle x1="36.9189" y1="2.5019" x2="38.4429" y2="2.5781" layer="200"/>
<rectangle x1="33.1089" y1="2.5781" x2="34.6329" y2="2.6543" layer="200"/>
<rectangle x1="37.0713" y1="2.5781" x2="38.5191" y2="2.6543" layer="200"/>
<rectangle x1="33.1089" y1="2.6543" x2="34.5567" y2="2.7305" layer="200"/>
<rectangle x1="37.2237" y1="2.6543" x2="38.6715" y2="2.7305" layer="200"/>
<rectangle x1="33.0327" y1="2.7305" x2="34.4043" y2="2.8067" layer="200"/>
<rectangle x1="37.3761" y1="2.7305" x2="38.7477" y2="2.8067" layer="200"/>
<rectangle x1="33.0327" y1="2.8067" x2="34.3281" y2="2.8829" layer="200"/>
<rectangle x1="37.5285" y1="2.8067" x2="38.8239" y2="2.8829" layer="200"/>
<rectangle x1="33.0327" y1="2.8829" x2="34.2519" y2="2.9591" layer="200"/>
<rectangle x1="37.6809" y1="2.8829" x2="38.9001" y2="2.9591" layer="200"/>
<rectangle x1="32.9565" y1="2.9591" x2="34.2519" y2="3.0353" layer="200"/>
<rectangle x1="37.7571" y1="2.9591" x2="38.9001" y2="3.0353" layer="200"/>
<rectangle x1="32.9565" y1="3.0353" x2="34.1757" y2="3.1115" layer="200"/>
<rectangle x1="37.8333" y1="3.0353" x2="38.9763" y2="3.1115" layer="200"/>
<rectangle x1="32.9565" y1="3.1115" x2="34.0995" y2="3.1877" layer="200"/>
<rectangle x1="37.9095" y1="3.1115" x2="39.0525" y2="3.1877" layer="200"/>
<rectangle x1="32.9565" y1="3.1877" x2="34.0995" y2="3.2639" layer="200"/>
<rectangle x1="37.9857" y1="3.1877" x2="39.1287" y2="3.2639" layer="200"/>
<rectangle x1="32.9565" y1="3.2639" x2="34.0995" y2="3.3401" layer="200"/>
<rectangle x1="38.0619" y1="3.2639" x2="39.1287" y2="3.3401" layer="200"/>
<rectangle x1="32.9565" y1="3.3401" x2="34.0995" y2="3.4163" layer="200"/>
<rectangle x1="38.1381" y1="3.3401" x2="39.2049" y2="3.4163" layer="200"/>
<rectangle x1="32.9565" y1="3.4163" x2="34.0233" y2="3.4925" layer="200"/>
<rectangle x1="38.2143" y1="3.4163" x2="39.2049" y2="3.4925" layer="200"/>
<rectangle x1="32.9565" y1="3.4925" x2="34.0233" y2="3.5687" layer="200"/>
<rectangle x1="38.2143" y1="3.4925" x2="39.2811" y2="3.5687" layer="200"/>
<rectangle x1="33.0327" y1="3.5687" x2="34.0995" y2="3.6449" layer="200"/>
<rectangle x1="38.2905" y1="3.5687" x2="39.2811" y2="3.6449" layer="200"/>
<rectangle x1="33.0327" y1="3.6449" x2="34.0995" y2="3.7211" layer="200"/>
<rectangle x1="38.2905" y1="3.6449" x2="39.2811" y2="3.7211" layer="200"/>
<rectangle x1="33.0327" y1="3.7211" x2="34.0995" y2="3.7973" layer="200"/>
<rectangle x1="38.3667" y1="3.7211" x2="39.3573" y2="3.7973" layer="200"/>
<rectangle x1="33.1089" y1="3.7973" x2="34.0995" y2="3.8735" layer="200"/>
<rectangle x1="38.3667" y1="3.7973" x2="39.3573" y2="3.8735" layer="200"/>
<rectangle x1="33.1089" y1="3.8735" x2="34.1757" y2="3.9497" layer="200"/>
<rectangle x1="38.3667" y1="3.8735" x2="39.3573" y2="3.9497" layer="200"/>
<rectangle x1="33.1851" y1="3.9497" x2="34.1757" y2="4.0259" layer="200"/>
<rectangle x1="38.3667" y1="3.9497" x2="39.3573" y2="4.0259" layer="200"/>
<rectangle x1="33.1851" y1="4.0259" x2="34.2519" y2="4.1021" layer="200"/>
<rectangle x1="38.3667" y1="4.0259" x2="39.3573" y2="4.1021" layer="200"/>
<rectangle x1="33.2613" y1="4.1021" x2="34.2519" y2="4.1783" layer="200"/>
<rectangle x1="38.3667" y1="4.1021" x2="39.4335" y2="4.1783" layer="200"/>
<rectangle x1="33.3375" y1="4.1783" x2="34.3281" y2="4.2545" layer="200"/>
<rectangle x1="38.3667" y1="4.1783" x2="39.4335" y2="4.2545" layer="200"/>
<rectangle x1="33.3375" y1="4.2545" x2="34.4043" y2="4.3307" layer="200"/>
<rectangle x1="38.3667" y1="4.2545" x2="39.4335" y2="4.3307" layer="200"/>
<rectangle x1="33.4137" y1="4.3307" x2="34.4805" y2="4.4069" layer="200"/>
<rectangle x1="38.3667" y1="4.3307" x2="39.4335" y2="4.4069" layer="200"/>
<rectangle x1="52.4637" y1="4.3307" x2="52.6923" y2="4.4069" layer="200"/>
<rectangle x1="33.4899" y1="4.4069" x2="34.4805" y2="4.4831" layer="200"/>
<rectangle x1="38.3667" y1="4.4069" x2="39.4335" y2="4.4831" layer="200"/>
<rectangle x1="43.3959" y1="4.4069" x2="44.5389" y2="4.4831" layer="200"/>
<rectangle x1="47.2059" y1="4.4069" x2="47.8917" y2="4.4831" layer="200"/>
<rectangle x1="52.0065" y1="4.4069" x2="52.6923" y2="4.4831" layer="200"/>
<rectangle x1="57.1881" y1="4.4069" x2="58.4073" y2="4.4831" layer="200"/>
<rectangle x1="69.6849" y1="4.4069" x2="71.3613" y2="4.4831" layer="200"/>
<rectangle x1="33.5661" y1="4.4831" x2="34.5567" y2="4.5593" layer="200"/>
<rectangle x1="38.2905" y1="4.4831" x2="39.4335" y2="4.5593" layer="200"/>
<rectangle x1="43.0911" y1="4.4831" x2="44.7675" y2="4.5593" layer="200"/>
<rectangle x1="46.9011" y1="4.4831" x2="47.9679" y2="4.5593" layer="200"/>
<rectangle x1="51.7779" y1="4.4831" x2="52.6923" y2="4.5593" layer="200"/>
<rectangle x1="56.8833" y1="4.4831" x2="58.7121" y2="4.5593" layer="200"/>
<rectangle x1="69.2277" y1="4.4831" x2="71.7423" y2="4.5593" layer="200"/>
<rectangle x1="33.6423" y1="4.5593" x2="34.6329" y2="4.6355" layer="200"/>
<rectangle x1="38.2905" y1="4.5593" x2="39.3573" y2="4.6355" layer="200"/>
<rectangle x1="42.9387" y1="4.5593" x2="44.9961" y2="4.6355" layer="200"/>
<rectangle x1="46.7487" y1="4.5593" x2="47.8917" y2="4.6355" layer="200"/>
<rectangle x1="51.5493" y1="4.5593" x2="52.6923" y2="4.6355" layer="200"/>
<rectangle x1="56.6547" y1="4.5593" x2="58.9407" y2="4.6355" layer="200"/>
<rectangle x1="64.1985" y1="4.5593" x2="65.1891" y2="4.6355" layer="200"/>
<rectangle x1="68.9229" y1="4.5593" x2="71.9709" y2="4.6355" layer="200"/>
<rectangle x1="33.7947" y1="4.6355" x2="34.7091" y2="4.7117" layer="200"/>
<rectangle x1="38.2143" y1="4.6355" x2="39.3573" y2="4.7117" layer="200"/>
<rectangle x1="42.7863" y1="4.6355" x2="45.1485" y2="4.7117" layer="200"/>
<rectangle x1="46.6725" y1="4.6355" x2="47.8917" y2="4.7117" layer="200"/>
<rectangle x1="51.3969" y1="4.6355" x2="52.6923" y2="4.7117" layer="200"/>
<rectangle x1="56.4261" y1="4.6355" x2="59.0931" y2="4.7117" layer="200"/>
<rectangle x1="64.1985" y1="4.6355" x2="65.1891" y2="4.7117" layer="200"/>
<rectangle x1="68.6943" y1="4.6355" x2="72.1233" y2="4.7117" layer="200"/>
<rectangle x1="33.8709" y1="4.7117" x2="34.7853" y2="4.7879" layer="200"/>
<rectangle x1="38.1381" y1="4.7117" x2="39.3573" y2="4.7879" layer="200"/>
<rectangle x1="42.6339" y1="4.7117" x2="45.3009" y2="4.7879" layer="200"/>
<rectangle x1="46.5201" y1="4.7117" x2="47.8917" y2="4.7879" layer="200"/>
<rectangle x1="51.3207" y1="4.7117" x2="52.6923" y2="4.7879" layer="200"/>
<rectangle x1="56.2737" y1="4.7117" x2="59.2455" y2="4.7879" layer="200"/>
<rectangle x1="64.1985" y1="4.7117" x2="65.1891" y2="4.7879" layer="200"/>
<rectangle x1="68.4657" y1="4.7117" x2="72.3519" y2="4.7879" layer="200"/>
<rectangle x1="33.9471" y1="4.7879" x2="34.8615" y2="4.8641" layer="200"/>
<rectangle x1="38.0619" y1="4.7879" x2="39.3573" y2="4.8641" layer="200"/>
<rectangle x1="42.4815" y1="4.7879" x2="45.4533" y2="4.8641" layer="200"/>
<rectangle x1="46.4439" y1="4.7879" x2="47.8917" y2="4.8641" layer="200"/>
<rectangle x1="51.1683" y1="4.7879" x2="52.6923" y2="4.8641" layer="200"/>
<rectangle x1="56.1975" y1="4.7879" x2="59.3979" y2="4.8641" layer="200"/>
<rectangle x1="64.1985" y1="4.7879" x2="65.1891" y2="4.8641" layer="200"/>
<rectangle x1="68.4657" y1="4.7879" x2="72.5043" y2="4.8641" layer="200"/>
<rectangle x1="34.0233" y1="4.8641" x2="34.9377" y2="4.9403" layer="200"/>
<rectangle x1="37.9095" y1="4.8641" x2="39.3573" y2="4.9403" layer="200"/>
<rectangle x1="42.4053" y1="4.8641" x2="45.6057" y2="4.9403" layer="200"/>
<rectangle x1="46.3677" y1="4.8641" x2="47.8917" y2="4.9403" layer="200"/>
<rectangle x1="51.0921" y1="4.8641" x2="52.6923" y2="4.9403" layer="200"/>
<rectangle x1="56.0451" y1="4.8641" x2="59.4741" y2="4.9403" layer="200"/>
<rectangle x1="64.1985" y1="4.8641" x2="65.1891" y2="4.9403" layer="200"/>
<rectangle x1="68.4657" y1="4.8641" x2="72.5805" y2="4.9403" layer="200"/>
<rectangle x1="34.0995" y1="4.9403" x2="36.6141" y2="5.0165" layer="200"/>
<rectangle x1="37.6047" y1="4.9403" x2="39.2811" y2="5.0165" layer="200"/>
<rectangle x1="42.3291" y1="4.9403" x2="45.6819" y2="5.0165" layer="200"/>
<rectangle x1="46.3677" y1="4.9403" x2="47.8917" y2="5.0165" layer="200"/>
<rectangle x1="51.0159" y1="4.9403" x2="52.6923" y2="5.0165" layer="200"/>
<rectangle x1="55.9689" y1="4.9403" x2="59.6265" y2="5.0165" layer="200"/>
<rectangle x1="64.1985" y1="4.9403" x2="65.1891" y2="5.0165" layer="200"/>
<rectangle x1="68.4657" y1="4.9403" x2="72.7329" y2="5.0165" layer="200"/>
<rectangle x1="33.8709" y1="5.0165" x2="39.2811" y2="5.0927" layer="200"/>
<rectangle x1="42.2529" y1="5.0165" x2="45.7581" y2="5.0927" layer="200"/>
<rectangle x1="46.2915" y1="5.0165" x2="47.8155" y2="5.0927" layer="200"/>
<rectangle x1="50.9397" y1="5.0165" x2="52.6923" y2="5.0927" layer="200"/>
<rectangle x1="55.8927" y1="5.0165" x2="59.7027" y2="5.0927" layer="200"/>
<rectangle x1="64.1985" y1="5.0165" x2="65.1891" y2="5.0927" layer="200"/>
<rectangle x1="68.5419" y1="5.0165" x2="72.8091" y2="5.0927" layer="200"/>
<rectangle x1="33.7185" y1="5.0927" x2="39.2049" y2="5.1689" layer="200"/>
<rectangle x1="42.1767" y1="5.0927" x2="45.8343" y2="5.1689" layer="200"/>
<rectangle x1="46.2915" y1="5.0927" x2="47.7393" y2="5.1689" layer="200"/>
<rectangle x1="50.8635" y1="5.0927" x2="52.6923" y2="5.1689" layer="200"/>
<rectangle x1="55.8165" y1="5.0927" x2="59.7789" y2="5.1689" layer="200"/>
<rectangle x1="64.1985" y1="5.0927" x2="65.1891" y2="5.1689" layer="200"/>
<rectangle x1="68.5419" y1="5.0927" x2="72.9615" y2="5.1689" layer="200"/>
<rectangle x1="33.6423" y1="5.1689" x2="39.2049" y2="5.2451" layer="200"/>
<rectangle x1="42.1767" y1="5.1689" x2="45.9867" y2="5.2451" layer="200"/>
<rectangle x1="46.2153" y1="5.1689" x2="47.6631" y2="5.2451" layer="200"/>
<rectangle x1="50.8635" y1="5.1689" x2="52.6923" y2="5.2451" layer="200"/>
<rectangle x1="55.6641" y1="5.1689" x2="59.8551" y2="5.2451" layer="200"/>
<rectangle x1="64.1985" y1="5.1689" x2="65.1891" y2="5.2451" layer="200"/>
<rectangle x1="68.5419" y1="5.1689" x2="70.2183" y2="5.2451" layer="200"/>
<rectangle x1="70.9803" y1="5.1689" x2="73.0377" y2="5.2451" layer="200"/>
<rectangle x1="33.4899" y1="5.2451" x2="39.1287" y2="5.3213" layer="200"/>
<rectangle x1="42.1005" y1="5.2451" x2="44.0055" y2="5.3213" layer="200"/>
<rectangle x1="44.3865" y1="5.2451" x2="46.0629" y2="5.3213" layer="200"/>
<rectangle x1="46.2153" y1="5.2451" x2="47.5869" y2="5.3213" layer="200"/>
<rectangle x1="50.7873" y1="5.2451" x2="52.6923" y2="5.3213" layer="200"/>
<rectangle x1="55.5879" y1="5.2451" x2="57.5691" y2="5.3213" layer="200"/>
<rectangle x1="58.0263" y1="5.2451" x2="59.9313" y2="5.3213" layer="200"/>
<rectangle x1="64.1985" y1="5.2451" x2="65.1891" y2="5.3213" layer="200"/>
<rectangle x1="68.5419" y1="5.2451" x2="69.6849" y2="5.3213" layer="200"/>
<rectangle x1="71.4375" y1="5.2451" x2="73.1139" y2="5.3213" layer="200"/>
<rectangle x1="33.4137" y1="5.3213" x2="39.1287" y2="5.3975" layer="200"/>
<rectangle x1="42.0243" y1="5.3213" x2="43.7007" y2="5.3975" layer="200"/>
<rectangle x1="44.7675" y1="5.3213" x2="47.5869" y2="5.3975" layer="200"/>
<rectangle x1="50.7111" y1="5.3213" x2="52.6923" y2="5.3975" layer="200"/>
<rectangle x1="55.5117" y1="5.3213" x2="57.1881" y2="5.3975" layer="200"/>
<rectangle x1="58.4073" y1="5.3213" x2="60.0075" y2="5.3975" layer="200"/>
<rectangle x1="64.1985" y1="5.3213" x2="65.1891" y2="5.3975" layer="200"/>
<rectangle x1="68.5419" y1="5.3213" x2="69.3039" y2="5.3975" layer="200"/>
<rectangle x1="71.6661" y1="5.3213" x2="73.1901" y2="5.3975" layer="200"/>
<rectangle x1="33.3375" y1="5.3975" x2="39.0525" y2="5.4737" layer="200"/>
<rectangle x1="42.0243" y1="5.3975" x2="43.5483" y2="5.4737" layer="200"/>
<rectangle x1="44.9961" y1="5.3975" x2="47.5107" y2="5.4737" layer="200"/>
<rectangle x1="50.7111" y1="5.3975" x2="52.6923" y2="5.4737" layer="200"/>
<rectangle x1="55.5117" y1="5.3975" x2="56.9595" y2="5.4737" layer="200"/>
<rectangle x1="58.6359" y1="5.3975" x2="60.0837" y2="5.4737" layer="200"/>
<rectangle x1="64.1985" y1="5.3975" x2="65.1891" y2="5.4737" layer="200"/>
<rectangle x1="68.6181" y1="5.3975" x2="69.0753" y2="5.4737" layer="200"/>
<rectangle x1="71.8947" y1="5.3975" x2="73.2663" y2="5.4737" layer="200"/>
<rectangle x1="33.3375" y1="5.4737" x2="38.9763" y2="5.5499" layer="200"/>
<rectangle x1="41.9481" y1="5.4737" x2="43.3959" y2="5.5499" layer="200"/>
<rectangle x1="45.1485" y1="5.4737" x2="47.5107" y2="5.5499" layer="200"/>
<rectangle x1="50.6349" y1="5.4737" x2="52.3875" y2="5.5499" layer="200"/>
<rectangle x1="55.4355" y1="5.4737" x2="56.8071" y2="5.5499" layer="200"/>
<rectangle x1="58.7883" y1="5.4737" x2="60.1599" y2="5.5499" layer="200"/>
<rectangle x1="64.1985" y1="5.4737" x2="65.1891" y2="5.5499" layer="200"/>
<rectangle x1="68.6181" y1="5.4737" x2="68.8467" y2="5.5499" layer="200"/>
<rectangle x1="72.0471" y1="5.4737" x2="73.2663" y2="5.5499" layer="200"/>
<rectangle x1="33.2613" y1="5.5499" x2="38.9001" y2="5.6261" layer="200"/>
<rectangle x1="41.9481" y1="5.5499" x2="43.3197" y2="5.6261" layer="200"/>
<rectangle x1="45.3009" y1="5.5499" x2="47.4345" y2="5.6261" layer="200"/>
<rectangle x1="50.6349" y1="5.5499" x2="52.1589" y2="5.6261" layer="200"/>
<rectangle x1="55.3593" y1="5.5499" x2="56.7309" y2="5.6261" layer="200"/>
<rectangle x1="58.8645" y1="5.5499" x2="60.1599" y2="5.6261" layer="200"/>
<rectangle x1="64.1985" y1="5.5499" x2="65.1891" y2="5.6261" layer="200"/>
<rectangle x1="68.6181" y1="5.5499" x2="68.6943" y2="5.6261" layer="200"/>
<rectangle x1="72.1233" y1="5.5499" x2="73.3425" y2="5.6261" layer="200"/>
<rectangle x1="33.2613" y1="5.6261" x2="38.8239" y2="5.7023" layer="200"/>
<rectangle x1="41.9481" y1="5.6261" x2="43.2435" y2="5.7023" layer="200"/>
<rectangle x1="45.4533" y1="5.6261" x2="47.4345" y2="5.7023" layer="200"/>
<rectangle x1="50.6349" y1="5.6261" x2="52.0065" y2="5.7023" layer="200"/>
<rectangle x1="55.2831" y1="5.6261" x2="56.5785" y2="5.7023" layer="200"/>
<rectangle x1="59.0169" y1="5.6261" x2="60.2361" y2="5.7023" layer="200"/>
<rectangle x1="64.1985" y1="5.6261" x2="65.1891" y2="5.7023" layer="200"/>
<rectangle x1="72.2757" y1="5.6261" x2="73.4187" y2="5.7023" layer="200"/>
<rectangle x1="33.1851" y1="5.7023" x2="38.6715" y2="5.7785" layer="200"/>
<rectangle x1="41.8719" y1="5.7023" x2="43.1673" y2="5.7785" layer="200"/>
<rectangle x1="45.5295" y1="5.7023" x2="47.4345" y2="5.7785" layer="200"/>
<rectangle x1="50.5587" y1="5.7023" x2="51.9303" y2="5.7785" layer="200"/>
<rectangle x1="55.2069" y1="5.7023" x2="56.5023" y2="5.7785" layer="200"/>
<rectangle x1="59.0931" y1="5.7023" x2="60.3123" y2="5.7785" layer="200"/>
<rectangle x1="64.1985" y1="5.7023" x2="65.1891" y2="5.7785" layer="200"/>
<rectangle x1="72.3519" y1="5.7023" x2="73.4187" y2="5.7785" layer="200"/>
<rectangle x1="33.1851" y1="5.7785" x2="38.5191" y2="5.8547" layer="200"/>
<rectangle x1="41.8719" y1="5.7785" x2="43.0911" y2="5.8547" layer="200"/>
<rectangle x1="45.6819" y1="5.7785" x2="47.3583" y2="5.8547" layer="200"/>
<rectangle x1="50.5587" y1="5.7785" x2="51.8541" y2="5.8547" layer="200"/>
<rectangle x1="55.2069" y1="5.7785" x2="56.4261" y2="5.8547" layer="200"/>
<rectangle x1="59.1693" y1="5.7785" x2="60.3885" y2="5.8547" layer="200"/>
<rectangle x1="64.1985" y1="5.7785" x2="65.1891" y2="5.8547" layer="200"/>
<rectangle x1="72.4281" y1="5.7785" x2="73.4949" y2="5.8547" layer="200"/>
<rectangle x1="33.1851" y1="5.8547" x2="38.3667" y2="5.9309" layer="200"/>
<rectangle x1="41.8719" y1="5.8547" x2="43.0149" y2="5.9309" layer="200"/>
<rectangle x1="45.7581" y1="5.8547" x2="47.3583" y2="5.9309" layer="200"/>
<rectangle x1="50.5587" y1="5.8547" x2="51.7779" y2="5.9309" layer="200"/>
<rectangle x1="55.1307" y1="5.8547" x2="56.3499" y2="5.9309" layer="200"/>
<rectangle x1="59.2455" y1="5.8547" x2="60.3885" y2="5.9309" layer="200"/>
<rectangle x1="64.1985" y1="5.8547" x2="65.1891" y2="5.9309" layer="200"/>
<rectangle x1="72.4281" y1="5.8547" x2="73.4949" y2="5.9309" layer="200"/>
<rectangle x1="33.1851" y1="5.9309" x2="34.6329" y2="6.0071" layer="200"/>
<rectangle x1="36.8427" y1="5.9309" x2="38.0619" y2="6.0071" layer="200"/>
<rectangle x1="41.8719" y1="5.9309" x2="42.9387" y2="6.0071" layer="200"/>
<rectangle x1="45.8343" y1="5.9309" x2="47.3583" y2="6.0071" layer="200"/>
<rectangle x1="50.5587" y1="5.9309" x2="51.7017" y2="6.0071" layer="200"/>
<rectangle x1="55.1307" y1="5.9309" x2="56.2737" y2="6.0071" layer="200"/>
<rectangle x1="59.3217" y1="5.9309" x2="60.4647" y2="6.0071" layer="200"/>
<rectangle x1="64.1985" y1="5.9309" x2="65.1891" y2="6.0071" layer="200"/>
<rectangle x1="72.5043" y1="5.9309" x2="73.5711" y2="6.0071" layer="200"/>
<rectangle x1="33.1851" y1="6.0071" x2="34.4805" y2="6.0833" layer="200"/>
<rectangle x1="41.7957" y1="6.0071" x2="42.9387" y2="6.0833" layer="200"/>
<rectangle x1="45.9105" y1="6.0071" x2="47.3583" y2="6.0833" layer="200"/>
<rectangle x1="50.4825" y1="6.0071" x2="51.7017" y2="6.0833" layer="200"/>
<rectangle x1="55.0545" y1="6.0071" x2="56.2737" y2="6.0833" layer="200"/>
<rectangle x1="59.3217" y1="6.0071" x2="60.4647" y2="6.0833" layer="200"/>
<rectangle x1="64.1985" y1="6.0071" x2="65.1891" y2="6.0833" layer="200"/>
<rectangle x1="72.5043" y1="6.0071" x2="73.5711" y2="6.0833" layer="200"/>
<rectangle x1="33.1851" y1="6.0833" x2="34.3281" y2="6.1595" layer="200"/>
<rectangle x1="41.7957" y1="6.0833" x2="42.9387" y2="6.1595" layer="200"/>
<rectangle x1="46.0629" y1="6.0833" x2="47.3583" y2="6.1595" layer="200"/>
<rectangle x1="50.4825" y1="6.0833" x2="51.6255" y2="6.1595" layer="200"/>
<rectangle x1="55.0545" y1="6.0833" x2="56.1975" y2="6.1595" layer="200"/>
<rectangle x1="59.3979" y1="6.0833" x2="60.5409" y2="6.1595" layer="200"/>
<rectangle x1="64.1985" y1="6.0833" x2="65.1891" y2="6.1595" layer="200"/>
<rectangle x1="72.5805" y1="6.0833" x2="73.5711" y2="6.1595" layer="200"/>
<rectangle x1="33.1851" y1="6.1595" x2="34.2519" y2="6.2357" layer="200"/>
<rectangle x1="41.7957" y1="6.1595" x2="42.8625" y2="6.2357" layer="200"/>
<rectangle x1="46.1391" y1="6.1595" x2="47.3583" y2="6.2357" layer="200"/>
<rectangle x1="50.4825" y1="6.1595" x2="51.6255" y2="6.2357" layer="200"/>
<rectangle x1="54.9783" y1="6.1595" x2="56.1213" y2="6.2357" layer="200"/>
<rectangle x1="59.4741" y1="6.1595" x2="60.6171" y2="6.2357" layer="200"/>
<rectangle x1="64.1985" y1="6.1595" x2="65.1891" y2="6.2357" layer="200"/>
<rectangle x1="72.5805" y1="6.1595" x2="73.5711" y2="6.2357" layer="200"/>
<rectangle x1="33.1851" y1="6.2357" x2="34.2519" y2="6.3119" layer="200"/>
<rectangle x1="41.7957" y1="6.2357" x2="42.8625" y2="6.3119" layer="200"/>
<rectangle x1="46.2153" y1="6.2357" x2="47.3583" y2="6.3119" layer="200"/>
<rectangle x1="50.4825" y1="6.2357" x2="51.5493" y2="6.3119" layer="200"/>
<rectangle x1="54.9783" y1="6.2357" x2="56.1213" y2="6.3119" layer="200"/>
<rectangle x1="59.4741" y1="6.2357" x2="60.6171" y2="6.3119" layer="200"/>
<rectangle x1="64.1985" y1="6.2357" x2="65.1891" y2="6.3119" layer="200"/>
<rectangle x1="72.5805" y1="6.2357" x2="73.5711" y2="6.3119" layer="200"/>
<rectangle x1="33.2613" y1="6.3119" x2="34.2519" y2="6.3881" layer="200"/>
<rectangle x1="41.7957" y1="6.3119" x2="42.8625" y2="6.3881" layer="200"/>
<rectangle x1="46.2915" y1="6.3119" x2="47.3583" y2="6.3881" layer="200"/>
<rectangle x1="50.4825" y1="6.3119" x2="51.5493" y2="6.3881" layer="200"/>
<rectangle x1="54.9021" y1="6.3119" x2="56.0451" y2="6.3881" layer="200"/>
<rectangle x1="59.5503" y1="6.3119" x2="60.6171" y2="6.3881" layer="200"/>
<rectangle x1="64.1985" y1="6.3119" x2="65.1891" y2="6.3881" layer="200"/>
<rectangle x1="72.5805" y1="6.3119" x2="73.6473" y2="6.3881" layer="200"/>
<rectangle x1="33.2613" y1="6.3881" x2="34.2519" y2="6.4643" layer="200"/>
<rectangle x1="41.7957" y1="6.3881" x2="42.8625" y2="6.4643" layer="200"/>
<rectangle x1="46.2915" y1="6.3881" x2="47.3583" y2="6.4643" layer="200"/>
<rectangle x1="50.4825" y1="6.3881" x2="51.5493" y2="6.4643" layer="200"/>
<rectangle x1="54.9021" y1="6.3881" x2="56.0451" y2="6.4643" layer="200"/>
<rectangle x1="59.5503" y1="6.3881" x2="60.6933" y2="6.4643" layer="200"/>
<rectangle x1="64.1985" y1="6.3881" x2="65.1891" y2="6.4643" layer="200"/>
<rectangle x1="72.5805" y1="6.3881" x2="73.6473" y2="6.4643" layer="200"/>
<rectangle x1="33.2613" y1="6.4643" x2="34.2519" y2="6.5405" layer="200"/>
<rectangle x1="41.7957" y1="6.4643" x2="42.8625" y2="6.5405" layer="200"/>
<rectangle x1="46.3677" y1="6.4643" x2="47.3583" y2="6.5405" layer="200"/>
<rectangle x1="50.4825" y1="6.4643" x2="51.4731" y2="6.5405" layer="200"/>
<rectangle x1="54.8259" y1="6.4643" x2="55.9689" y2="6.5405" layer="200"/>
<rectangle x1="59.6265" y1="6.4643" x2="60.6933" y2="6.5405" layer="200"/>
<rectangle x1="64.1985" y1="6.4643" x2="65.1891" y2="6.5405" layer="200"/>
<rectangle x1="72.5805" y1="6.4643" x2="73.6473" y2="6.5405" layer="200"/>
<rectangle x1="33.3375" y1="6.5405" x2="34.3281" y2="6.6167" layer="200"/>
<rectangle x1="41.7957" y1="6.5405" x2="42.8625" y2="6.6167" layer="200"/>
<rectangle x1="46.3677" y1="6.5405" x2="47.3583" y2="6.6167" layer="200"/>
<rectangle x1="50.4825" y1="6.5405" x2="51.4731" y2="6.6167" layer="200"/>
<rectangle x1="54.8259" y1="6.5405" x2="55.9689" y2="6.6167" layer="200"/>
<rectangle x1="59.6265" y1="6.5405" x2="60.7695" y2="6.6167" layer="200"/>
<rectangle x1="64.1985" y1="6.5405" x2="65.1891" y2="6.6167" layer="200"/>
<rectangle x1="72.5805" y1="6.5405" x2="73.6473" y2="6.6167" layer="200"/>
<rectangle x1="33.4137" y1="6.6167" x2="34.3281" y2="6.6929" layer="200"/>
<rectangle x1="41.8719" y1="6.6167" x2="42.8625" y2="6.6929" layer="200"/>
<rectangle x1="46.3677" y1="6.6167" x2="47.3583" y2="6.6929" layer="200"/>
<rectangle x1="50.4825" y1="6.6167" x2="51.4731" y2="6.6929" layer="200"/>
<rectangle x1="54.8259" y1="6.6167" x2="55.8927" y2="6.6929" layer="200"/>
<rectangle x1="59.7027" y1="6.6167" x2="60.7695" y2="6.6929" layer="200"/>
<rectangle x1="64.1985" y1="6.6167" x2="65.1891" y2="6.6929" layer="200"/>
<rectangle x1="72.5805" y1="6.6167" x2="73.6473" y2="6.6929" layer="200"/>
<rectangle x1="33.4899" y1="6.6929" x2="34.4043" y2="6.7691" layer="200"/>
<rectangle x1="41.8719" y1="6.6929" x2="42.8625" y2="6.7691" layer="200"/>
<rectangle x1="46.3677" y1="6.6929" x2="47.3583" y2="6.7691" layer="200"/>
<rectangle x1="50.4825" y1="6.6929" x2="51.4731" y2="6.7691" layer="200"/>
<rectangle x1="54.7497" y1="6.6929" x2="55.8927" y2="6.7691" layer="200"/>
<rectangle x1="59.7027" y1="6.6929" x2="60.7695" y2="6.7691" layer="200"/>
<rectangle x1="64.1985" y1="6.6929" x2="65.1891" y2="6.7691" layer="200"/>
<rectangle x1="72.5805" y1="6.6929" x2="73.6473" y2="6.7691" layer="200"/>
<rectangle x1="33.5661" y1="6.7691" x2="34.4805" y2="6.8453" layer="200"/>
<rectangle x1="41.8719" y1="6.7691" x2="42.9387" y2="6.8453" layer="200"/>
<rectangle x1="46.3677" y1="6.7691" x2="47.3583" y2="6.8453" layer="200"/>
<rectangle x1="50.4825" y1="6.7691" x2="51.4731" y2="6.8453" layer="200"/>
<rectangle x1="54.7497" y1="6.7691" x2="55.8165" y2="6.8453" layer="200"/>
<rectangle x1="59.7027" y1="6.7691" x2="60.8457" y2="6.8453" layer="200"/>
<rectangle x1="64.1985" y1="6.7691" x2="65.1891" y2="6.8453" layer="200"/>
<rectangle x1="72.5805" y1="6.7691" x2="73.6473" y2="6.8453" layer="200"/>
<rectangle x1="33.6423" y1="6.8453" x2="34.6329" y2="6.9215" layer="200"/>
<rectangle x1="41.8719" y1="6.8453" x2="42.9387" y2="6.9215" layer="200"/>
<rectangle x1="46.3677" y1="6.8453" x2="47.3583" y2="6.9215" layer="200"/>
<rectangle x1="50.4825" y1="6.8453" x2="51.4731" y2="6.9215" layer="200"/>
<rectangle x1="54.7497" y1="6.8453" x2="55.8165" y2="6.9215" layer="200"/>
<rectangle x1="59.7789" y1="6.8453" x2="60.8457" y2="6.9215" layer="200"/>
<rectangle x1="64.1985" y1="6.8453" x2="65.1891" y2="6.9215" layer="200"/>
<rectangle x1="72.5043" y1="6.8453" x2="73.6473" y2="6.9215" layer="200"/>
<rectangle x1="33.7185" y1="6.9215" x2="34.7091" y2="6.9977" layer="200"/>
<rectangle x1="41.8719" y1="6.9215" x2="42.9387" y2="6.9977" layer="200"/>
<rectangle x1="46.3677" y1="6.9215" x2="47.3583" y2="6.9977" layer="200"/>
<rectangle x1="50.4825" y1="6.9215" x2="51.4731" y2="6.9977" layer="200"/>
<rectangle x1="54.6735" y1="6.9215" x2="55.8165" y2="6.9977" layer="200"/>
<rectangle x1="59.7789" y1="6.9215" x2="60.8457" y2="6.9977" layer="200"/>
<rectangle x1="64.1985" y1="6.9215" x2="65.1891" y2="6.9977" layer="200"/>
<rectangle x1="72.5043" y1="6.9215" x2="73.5711" y2="6.9977" layer="200"/>
<rectangle x1="33.7947" y1="6.9977" x2="34.7853" y2="7.0739" layer="200"/>
<rectangle x1="41.9481" y1="6.9977" x2="43.0149" y2="7.0739" layer="200"/>
<rectangle x1="46.3677" y1="6.9977" x2="47.3583" y2="7.0739" layer="200"/>
<rectangle x1="50.4825" y1="6.9977" x2="51.4731" y2="7.0739" layer="200"/>
<rectangle x1="54.6735" y1="6.9977" x2="55.8165" y2="7.0739" layer="200"/>
<rectangle x1="59.7789" y1="6.9977" x2="60.9219" y2="7.0739" layer="200"/>
<rectangle x1="64.1985" y1="6.9977" x2="65.1891" y2="7.0739" layer="200"/>
<rectangle x1="72.4281" y1="6.9977" x2="73.5711" y2="7.0739" layer="200"/>
<rectangle x1="33.9471" y1="7.0739" x2="34.9377" y2="7.1501" layer="200"/>
<rectangle x1="41.9481" y1="7.0739" x2="43.0149" y2="7.1501" layer="200"/>
<rectangle x1="46.3677" y1="7.0739" x2="47.3583" y2="7.1501" layer="200"/>
<rectangle x1="50.4825" y1="7.0739" x2="51.4731" y2="7.1501" layer="200"/>
<rectangle x1="54.6735" y1="7.0739" x2="55.7403" y2="7.1501" layer="200"/>
<rectangle x1="59.8551" y1="7.0739" x2="60.9219" y2="7.1501" layer="200"/>
<rectangle x1="64.1985" y1="7.0739" x2="65.1891" y2="7.1501" layer="200"/>
<rectangle x1="72.3519" y1="7.0739" x2="73.5711" y2="7.1501" layer="200"/>
<rectangle x1="34.0233" y1="7.1501" x2="35.0139" y2="7.2263" layer="200"/>
<rectangle x1="42.0243" y1="7.1501" x2="43.0911" y2="7.2263" layer="200"/>
<rectangle x1="46.3677" y1="7.1501" x2="47.3583" y2="7.2263" layer="200"/>
<rectangle x1="50.4825" y1="7.1501" x2="51.4731" y2="7.2263" layer="200"/>
<rectangle x1="54.6735" y1="7.1501" x2="55.7403" y2="7.2263" layer="200"/>
<rectangle x1="59.8551" y1="7.1501" x2="60.9219" y2="7.2263" layer="200"/>
<rectangle x1="64.1985" y1="7.1501" x2="65.1891" y2="7.2263" layer="200"/>
<rectangle x1="72.2757" y1="7.1501" x2="73.5711" y2="7.2263" layer="200"/>
<rectangle x1="34.0995" y1="7.2263" x2="36.2331" y2="7.3025" layer="200"/>
<rectangle x1="42.0243" y1="7.2263" x2="43.1673" y2="7.3025" layer="200"/>
<rectangle x1="46.3677" y1="7.2263" x2="47.3583" y2="7.3025" layer="200"/>
<rectangle x1="50.4825" y1="7.2263" x2="51.4731" y2="7.3025" layer="200"/>
<rectangle x1="54.6735" y1="7.2263" x2="55.7403" y2="7.3025" layer="200"/>
<rectangle x1="59.8551" y1="7.2263" x2="60.9219" y2="7.3025" layer="200"/>
<rectangle x1="64.1985" y1="7.2263" x2="65.1891" y2="7.3025" layer="200"/>
<rectangle x1="72.1995" y1="7.2263" x2="73.4949" y2="7.3025" layer="200"/>
<rectangle x1="34.2519" y1="7.3025" x2="36.5379" y2="7.3787" layer="200"/>
<rectangle x1="42.1005" y1="7.3025" x2="43.2435" y2="7.3787" layer="200"/>
<rectangle x1="46.3677" y1="7.3025" x2="47.3583" y2="7.3787" layer="200"/>
<rectangle x1="50.4825" y1="7.3025" x2="51.4731" y2="7.3787" layer="200"/>
<rectangle x1="54.5973" y1="7.3025" x2="55.7403" y2="7.3787" layer="200"/>
<rectangle x1="59.8551" y1="7.3025" x2="60.9219" y2="7.3787" layer="200"/>
<rectangle x1="64.1985" y1="7.3025" x2="65.1891" y2="7.3787" layer="200"/>
<rectangle x1="72.1233" y1="7.3025" x2="73.4949" y2="7.3787" layer="200"/>
<rectangle x1="34.3281" y1="7.3787" x2="36.7665" y2="7.4549" layer="200"/>
<rectangle x1="42.1005" y1="7.3787" x2="43.3197" y2="7.4549" layer="200"/>
<rectangle x1="46.3677" y1="7.3787" x2="47.3583" y2="7.4549" layer="200"/>
<rectangle x1="50.4825" y1="7.3787" x2="51.4731" y2="7.4549" layer="200"/>
<rectangle x1="54.5973" y1="7.3787" x2="55.6641" y2="7.4549" layer="200"/>
<rectangle x1="59.8551" y1="7.3787" x2="60.9219" y2="7.4549" layer="200"/>
<rectangle x1="64.1985" y1="7.3787" x2="65.1891" y2="7.4549" layer="200"/>
<rectangle x1="71.9709" y1="7.3787" x2="73.4187" y2="7.4549" layer="200"/>
<rectangle x1="34.3281" y1="7.4549" x2="36.9189" y2="7.5311" layer="200"/>
<rectangle x1="42.1767" y1="7.4549" x2="43.3959" y2="7.5311" layer="200"/>
<rectangle x1="46.3677" y1="7.4549" x2="47.3583" y2="7.5311" layer="200"/>
<rectangle x1="50.4825" y1="7.4549" x2="51.4731" y2="7.5311" layer="200"/>
<rectangle x1="54.5973" y1="7.4549" x2="55.6641" y2="7.5311" layer="200"/>
<rectangle x1="59.8551" y1="7.4549" x2="60.9981" y2="7.5311" layer="200"/>
<rectangle x1="64.1985" y1="7.4549" x2="65.1891" y2="7.5311" layer="200"/>
<rectangle x1="71.8185" y1="7.4549" x2="73.4187" y2="7.5311" layer="200"/>
<rectangle x1="34.2519" y1="7.5311" x2="37.0713" y2="7.6073" layer="200"/>
<rectangle x1="42.2529" y1="7.5311" x2="43.5483" y2="7.6073" layer="200"/>
<rectangle x1="46.3677" y1="7.5311" x2="47.3583" y2="7.6073" layer="200"/>
<rectangle x1="50.4825" y1="7.5311" x2="51.4731" y2="7.6073" layer="200"/>
<rectangle x1="54.5973" y1="7.5311" x2="55.6641" y2="7.6073" layer="200"/>
<rectangle x1="59.9313" y1="7.5311" x2="60.9981" y2="7.6073" layer="200"/>
<rectangle x1="64.1985" y1="7.5311" x2="65.1891" y2="7.6073" layer="200"/>
<rectangle x1="71.6661" y1="7.5311" x2="73.3425" y2="7.6073" layer="200"/>
<rectangle x1="34.1757" y1="7.6073" x2="37.2237" y2="7.6835" layer="200"/>
<rectangle x1="42.3291" y1="7.6073" x2="43.7007" y2="7.6835" layer="200"/>
<rectangle x1="46.3677" y1="7.6073" x2="47.3583" y2="7.6835" layer="200"/>
<rectangle x1="50.4825" y1="7.6073" x2="51.4731" y2="7.6835" layer="200"/>
<rectangle x1="54.5973" y1="7.6073" x2="55.6641" y2="7.6835" layer="200"/>
<rectangle x1="59.9313" y1="7.6073" x2="60.9981" y2="7.6835" layer="200"/>
<rectangle x1="64.1985" y1="7.6073" x2="65.1891" y2="7.6835" layer="200"/>
<rectangle x1="71.4375" y1="7.6073" x2="73.3425" y2="7.6835" layer="200"/>
<rectangle x1="34.0233" y1="7.6835" x2="37.2999" y2="7.7597" layer="200"/>
<rectangle x1="42.4053" y1="7.6835" x2="43.8531" y2="7.7597" layer="200"/>
<rectangle x1="46.3677" y1="7.6835" x2="47.3583" y2="7.7597" layer="200"/>
<rectangle x1="50.4825" y1="7.6835" x2="51.4731" y2="7.7597" layer="200"/>
<rectangle x1="54.5973" y1="7.6835" x2="55.6641" y2="7.7597" layer="200"/>
<rectangle x1="59.9313" y1="7.6835" x2="60.9981" y2="7.7597" layer="200"/>
<rectangle x1="64.1985" y1="7.6835" x2="65.1891" y2="7.7597" layer="200"/>
<rectangle x1="71.2089" y1="7.6835" x2="73.2663" y2="7.7597" layer="200"/>
<rectangle x1="33.9471" y1="7.7597" x2="37.3761" y2="7.8359" layer="200"/>
<rectangle x1="42.4815" y1="7.7597" x2="44.0817" y2="7.8359" layer="200"/>
<rectangle x1="46.3677" y1="7.7597" x2="47.3583" y2="7.8359" layer="200"/>
<rectangle x1="50.4825" y1="7.7597" x2="51.4731" y2="7.8359" layer="200"/>
<rectangle x1="54.5973" y1="7.7597" x2="55.6641" y2="7.8359" layer="200"/>
<rectangle x1="59.9313" y1="7.7597" x2="60.9981" y2="7.8359" layer="200"/>
<rectangle x1="64.1985" y1="7.7597" x2="65.1891" y2="7.8359" layer="200"/>
<rectangle x1="70.9041" y1="7.7597" x2="73.1901" y2="7.8359" layer="200"/>
<rectangle x1="33.8709" y1="7.8359" x2="37.5285" y2="7.9121" layer="200"/>
<rectangle x1="42.5577" y1="7.8359" x2="44.3103" y2="7.9121" layer="200"/>
<rectangle x1="46.3677" y1="7.8359" x2="47.3583" y2="7.9121" layer="200"/>
<rectangle x1="50.4825" y1="7.8359" x2="51.4731" y2="7.9121" layer="200"/>
<rectangle x1="54.5973" y1="7.8359" x2="55.6641" y2="7.9121" layer="200"/>
<rectangle x1="59.9313" y1="7.8359" x2="60.9981" y2="7.9121" layer="200"/>
<rectangle x1="64.1985" y1="7.8359" x2="65.1891" y2="7.9121" layer="200"/>
<rectangle x1="70.6755" y1="7.8359" x2="73.1139" y2="7.9121" layer="200"/>
<rectangle x1="33.7947" y1="7.9121" x2="35.5473" y2="7.9883" layer="200"/>
<rectangle x1="36.0045" y1="7.9121" x2="37.6047" y2="7.9883" layer="200"/>
<rectangle x1="42.6339" y1="7.9121" x2="44.7675" y2="7.9883" layer="200"/>
<rectangle x1="46.3677" y1="7.9121" x2="47.3583" y2="7.9883" layer="200"/>
<rectangle x1="50.4825" y1="7.9121" x2="51.4731" y2="7.9883" layer="200"/>
<rectangle x1="54.5973" y1="7.9121" x2="55.6641" y2="7.9883" layer="200"/>
<rectangle x1="59.9313" y1="7.9121" x2="60.9981" y2="7.9883" layer="200"/>
<rectangle x1="64.1985" y1="7.9121" x2="65.1891" y2="7.9883" layer="200"/>
<rectangle x1="70.4469" y1="7.9121" x2="73.0377" y2="7.9883" layer="200"/>
<rectangle x1="33.7947" y1="7.9883" x2="35.2425" y2="8.0645" layer="200"/>
<rectangle x1="36.3093" y1="7.9883" x2="37.6809" y2="8.0645" layer="200"/>
<rectangle x1="42.7863" y1="7.9883" x2="45.5295" y2="8.0645" layer="200"/>
<rectangle x1="46.3677" y1="7.9883" x2="47.3583" y2="8.0645" layer="200"/>
<rectangle x1="50.4825" y1="7.9883" x2="51.4731" y2="8.0645" layer="200"/>
<rectangle x1="54.5973" y1="7.9883" x2="55.6641" y2="8.0645" layer="200"/>
<rectangle x1="59.9313" y1="7.9883" x2="60.9981" y2="8.0645" layer="200"/>
<rectangle x1="64.1985" y1="7.9883" x2="65.1891" y2="8.0645" layer="200"/>
<rectangle x1="70.2183" y1="7.9883" x2="72.9615" y2="8.0645" layer="200"/>
<rectangle x1="33.7185" y1="8.0645" x2="35.0901" y2="8.1407" layer="200"/>
<rectangle x1="36.4617" y1="8.0645" x2="37.7571" y2="8.1407" layer="200"/>
<rectangle x1="42.8625" y1="8.0645" x2="47.3583" y2="8.1407" layer="200"/>
<rectangle x1="50.4825" y1="8.0645" x2="51.4731" y2="8.1407" layer="200"/>
<rectangle x1="54.5973" y1="8.0645" x2="55.6641" y2="8.1407" layer="200"/>
<rectangle x1="59.9313" y1="8.0645" x2="60.9981" y2="8.1407" layer="200"/>
<rectangle x1="64.1985" y1="8.0645" x2="65.1891" y2="8.1407" layer="200"/>
<rectangle x1="69.9135" y1="8.0645" x2="72.8091" y2="8.1407" layer="200"/>
<rectangle x1="33.6423" y1="8.1407" x2="34.9377" y2="8.2169" layer="200"/>
<rectangle x1="36.5379" y1="8.1407" x2="37.7571" y2="8.2169" layer="200"/>
<rectangle x1="43.0149" y1="8.1407" x2="47.3583" y2="8.2169" layer="200"/>
<rectangle x1="50.4825" y1="8.1407" x2="51.4731" y2="8.2169" layer="200"/>
<rectangle x1="54.5973" y1="8.1407" x2="55.6641" y2="8.2169" layer="200"/>
<rectangle x1="59.9313" y1="8.1407" x2="60.9981" y2="8.2169" layer="200"/>
<rectangle x1="64.1985" y1="8.1407" x2="65.1891" y2="8.2169" layer="200"/>
<rectangle x1="69.6849" y1="8.1407" x2="72.7329" y2="8.2169" layer="200"/>
<rectangle x1="33.5661" y1="8.2169" x2="34.8615" y2="8.2931" layer="200"/>
<rectangle x1="36.6903" y1="8.2169" x2="37.8333" y2="8.2931" layer="200"/>
<rectangle x1="43.1673" y1="8.2169" x2="47.3583" y2="8.2931" layer="200"/>
<rectangle x1="50.4825" y1="8.2169" x2="51.4731" y2="8.2931" layer="200"/>
<rectangle x1="54.5973" y1="8.2169" x2="55.6641" y2="8.2931" layer="200"/>
<rectangle x1="59.9313" y1="8.2169" x2="60.9981" y2="8.2931" layer="200"/>
<rectangle x1="64.1985" y1="8.2169" x2="65.1891" y2="8.2931" layer="200"/>
<rectangle x1="69.5325" y1="8.2169" x2="72.5805" y2="8.2931" layer="200"/>
<rectangle x1="33.5661" y1="8.2931" x2="34.7853" y2="8.3693" layer="200"/>
<rectangle x1="36.7665" y1="8.2931" x2="37.9095" y2="8.3693" layer="200"/>
<rectangle x1="43.3197" y1="8.2931" x2="47.3583" y2="8.3693" layer="200"/>
<rectangle x1="50.4825" y1="8.2931" x2="51.4731" y2="8.3693" layer="200"/>
<rectangle x1="54.5973" y1="8.2931" x2="55.6641" y2="8.3693" layer="200"/>
<rectangle x1="59.9313" y1="8.2931" x2="60.9981" y2="8.3693" layer="200"/>
<rectangle x1="64.1985" y1="8.2931" x2="65.1891" y2="8.3693" layer="200"/>
<rectangle x1="69.3801" y1="8.2931" x2="72.4281" y2="8.3693" layer="200"/>
<rectangle x1="33.4899" y1="8.3693" x2="34.7091" y2="8.4455" layer="200"/>
<rectangle x1="36.8427" y1="8.3693" x2="37.9857" y2="8.4455" layer="200"/>
<rectangle x1="43.5483" y1="8.3693" x2="47.3583" y2="8.4455" layer="200"/>
<rectangle x1="50.4825" y1="8.3693" x2="51.4731" y2="8.4455" layer="200"/>
<rectangle x1="54.5973" y1="8.3693" x2="55.6641" y2="8.4455" layer="200"/>
<rectangle x1="59.9313" y1="8.3693" x2="60.9981" y2="8.4455" layer="200"/>
<rectangle x1="64.1985" y1="8.3693" x2="65.1891" y2="8.4455" layer="200"/>
<rectangle x1="69.2277" y1="8.3693" x2="72.2757" y2="8.4455" layer="200"/>
<rectangle x1="33.4899" y1="8.4455" x2="34.6329" y2="8.5217" layer="200"/>
<rectangle x1="36.9189" y1="8.4455" x2="37.9857" y2="8.5217" layer="200"/>
<rectangle x1="43.7769" y1="8.4455" x2="47.3583" y2="8.5217" layer="200"/>
<rectangle x1="50.4825" y1="8.4455" x2="51.4731" y2="8.5217" layer="200"/>
<rectangle x1="54.5973" y1="8.4455" x2="55.6641" y2="8.5217" layer="200"/>
<rectangle x1="59.9313" y1="8.4455" x2="60.9981" y2="8.5217" layer="200"/>
<rectangle x1="64.1985" y1="8.4455" x2="65.1891" y2="8.5217" layer="200"/>
<rectangle x1="69.0753" y1="8.4455" x2="72.0471" y2="8.5217" layer="200"/>
<rectangle x1="33.4137" y1="8.5217" x2="34.5567" y2="8.5979" layer="200"/>
<rectangle x1="36.9189" y1="8.5217" x2="38.0619" y2="8.5979" layer="200"/>
<rectangle x1="44.0055" y1="8.5217" x2="47.3583" y2="8.5979" layer="200"/>
<rectangle x1="50.4825" y1="8.5217" x2="51.4731" y2="8.5979" layer="200"/>
<rectangle x1="54.5973" y1="8.5217" x2="55.6641" y2="8.5979" layer="200"/>
<rectangle x1="59.9313" y1="8.5217" x2="60.9981" y2="8.5979" layer="200"/>
<rectangle x1="64.1985" y1="8.5217" x2="65.1891" y2="8.5979" layer="200"/>
<rectangle x1="68.9991" y1="8.5217" x2="71.8185" y2="8.5979" layer="200"/>
<rectangle x1="33.4137" y1="8.5979" x2="34.4805" y2="8.6741" layer="200"/>
<rectangle x1="36.9951" y1="8.5979" x2="38.0619" y2="8.6741" layer="200"/>
<rectangle x1="44.3865" y1="8.5979" x2="47.3583" y2="8.6741" layer="200"/>
<rectangle x1="50.4825" y1="8.5979" x2="51.4731" y2="8.6741" layer="200"/>
<rectangle x1="54.5973" y1="8.5979" x2="55.6641" y2="8.6741" layer="200"/>
<rectangle x1="59.9313" y1="8.5979" x2="60.9981" y2="8.6741" layer="200"/>
<rectangle x1="64.1985" y1="8.5979" x2="65.1891" y2="8.6741" layer="200"/>
<rectangle x1="68.9229" y1="8.5979" x2="71.5899" y2="8.6741" layer="200"/>
<rectangle x1="33.4137" y1="8.6741" x2="34.4805" y2="8.7503" layer="200"/>
<rectangle x1="37.0713" y1="8.6741" x2="38.1381" y2="8.7503" layer="200"/>
<rectangle x1="45.1485" y1="8.6741" x2="47.3583" y2="8.7503" layer="200"/>
<rectangle x1="50.4825" y1="8.6741" x2="51.4731" y2="8.7503" layer="200"/>
<rectangle x1="54.5973" y1="8.6741" x2="55.6641" y2="8.7503" layer="200"/>
<rectangle x1="59.9313" y1="8.6741" x2="60.9981" y2="8.7503" layer="200"/>
<rectangle x1="64.1985" y1="8.6741" x2="65.1891" y2="8.7503" layer="200"/>
<rectangle x1="68.8467" y1="8.6741" x2="71.3613" y2="8.7503" layer="200"/>
<rectangle x1="33.3375" y1="8.7503" x2="34.4043" y2="8.8265" layer="200"/>
<rectangle x1="37.0713" y1="8.7503" x2="38.1381" y2="8.8265" layer="200"/>
<rectangle x1="46.1391" y1="8.7503" x2="47.3583" y2="8.8265" layer="200"/>
<rectangle x1="50.4825" y1="8.7503" x2="51.4731" y2="8.8265" layer="200"/>
<rectangle x1="54.5973" y1="8.7503" x2="55.6641" y2="8.8265" layer="200"/>
<rectangle x1="59.9313" y1="8.7503" x2="60.9981" y2="8.8265" layer="200"/>
<rectangle x1="64.1985" y1="8.7503" x2="65.1891" y2="8.8265" layer="200"/>
<rectangle x1="68.7705" y1="8.7503" x2="71.1327" y2="8.8265" layer="200"/>
<rectangle x1="33.3375" y1="8.8265" x2="34.4043" y2="8.9027" layer="200"/>
<rectangle x1="37.1475" y1="8.8265" x2="38.1381" y2="8.9027" layer="200"/>
<rectangle x1="46.3677" y1="8.8265" x2="47.3583" y2="8.9027" layer="200"/>
<rectangle x1="50.4825" y1="8.8265" x2="51.4731" y2="8.9027" layer="200"/>
<rectangle x1="54.5973" y1="8.8265" x2="55.7403" y2="8.9027" layer="200"/>
<rectangle x1="59.8551" y1="8.8265" x2="60.9981" y2="8.9027" layer="200"/>
<rectangle x1="64.1985" y1="8.8265" x2="65.1891" y2="8.9027" layer="200"/>
<rectangle x1="68.6943" y1="8.8265" x2="70.8279" y2="8.9027" layer="200"/>
<rectangle x1="33.3375" y1="8.9027" x2="34.3281" y2="8.9789" layer="200"/>
<rectangle x1="37.1475" y1="8.9027" x2="38.2143" y2="8.9789" layer="200"/>
<rectangle x1="46.3677" y1="8.9027" x2="47.3583" y2="8.9789" layer="200"/>
<rectangle x1="50.4825" y1="8.9027" x2="51.4731" y2="8.9789" layer="200"/>
<rectangle x1="54.5973" y1="8.9027" x2="55.7403" y2="8.9789" layer="200"/>
<rectangle x1="59.8551" y1="8.9027" x2="60.9219" y2="8.9789" layer="200"/>
<rectangle x1="64.1985" y1="8.9027" x2="65.1891" y2="8.9789" layer="200"/>
<rectangle x1="68.6181" y1="8.9027" x2="70.5993" y2="8.9789" layer="200"/>
<rectangle x1="33.2613" y1="8.9789" x2="34.3281" y2="9.0551" layer="200"/>
<rectangle x1="37.1475" y1="8.9789" x2="38.2143" y2="9.0551" layer="200"/>
<rectangle x1="46.3677" y1="8.9789" x2="47.3583" y2="9.0551" layer="200"/>
<rectangle x1="50.4825" y1="8.9789" x2="51.4731" y2="9.0551" layer="200"/>
<rectangle x1="54.6735" y1="8.9789" x2="55.7403" y2="9.0551" layer="200"/>
<rectangle x1="59.8551" y1="8.9789" x2="60.9219" y2="9.0551" layer="200"/>
<rectangle x1="64.1985" y1="8.9789" x2="65.1891" y2="9.0551" layer="200"/>
<rectangle x1="68.6181" y1="8.9789" x2="70.3707" y2="9.0551" layer="200"/>
<rectangle x1="33.2613" y1="9.0551" x2="34.3281" y2="9.1313" layer="200"/>
<rectangle x1="37.2237" y1="9.0551" x2="38.2143" y2="9.1313" layer="200"/>
<rectangle x1="46.3677" y1="9.0551" x2="47.3583" y2="9.1313" layer="200"/>
<rectangle x1="50.4825" y1="9.0551" x2="51.4731" y2="9.1313" layer="200"/>
<rectangle x1="54.6735" y1="9.0551" x2="55.7403" y2="9.1313" layer="200"/>
<rectangle x1="59.8551" y1="9.0551" x2="60.9219" y2="9.1313" layer="200"/>
<rectangle x1="64.1985" y1="9.0551" x2="65.1891" y2="9.1313" layer="200"/>
<rectangle x1="68.5419" y1="9.0551" x2="70.1421" y2="9.1313" layer="200"/>
<rectangle x1="33.2613" y1="9.1313" x2="34.2519" y2="9.2075" layer="200"/>
<rectangle x1="37.2237" y1="9.1313" x2="38.2143" y2="9.2075" layer="200"/>
<rectangle x1="46.3677" y1="9.1313" x2="47.3583" y2="9.2075" layer="200"/>
<rectangle x1="50.4825" y1="9.1313" x2="51.4731" y2="9.2075" layer="200"/>
<rectangle x1="54.6735" y1="9.1313" x2="55.7403" y2="9.2075" layer="200"/>
<rectangle x1="59.8551" y1="9.1313" x2="60.9219" y2="9.2075" layer="200"/>
<rectangle x1="64.1985" y1="9.1313" x2="65.1891" y2="9.2075" layer="200"/>
<rectangle x1="68.4657" y1="9.1313" x2="69.9897" y2="9.2075" layer="200"/>
<rectangle x1="33.2613" y1="9.2075" x2="34.2519" y2="9.2837" layer="200"/>
<rectangle x1="37.2237" y1="9.2075" x2="38.2143" y2="9.2837" layer="200"/>
<rectangle x1="46.3677" y1="9.2075" x2="47.3583" y2="9.2837" layer="200"/>
<rectangle x1="50.4825" y1="9.2075" x2="51.4731" y2="9.2837" layer="200"/>
<rectangle x1="54.6735" y1="9.2075" x2="55.8165" y2="9.2837" layer="200"/>
<rectangle x1="59.7789" y1="9.2075" x2="60.9219" y2="9.2837" layer="200"/>
<rectangle x1="64.1985" y1="9.2075" x2="65.1891" y2="9.2837" layer="200"/>
<rectangle x1="68.4657" y1="9.2075" x2="69.8373" y2="9.2837" layer="200"/>
<rectangle x1="33.2613" y1="9.2837" x2="34.2519" y2="9.3599" layer="200"/>
<rectangle x1="37.2237" y1="9.2837" x2="38.2143" y2="9.3599" layer="200"/>
<rectangle x1="46.3677" y1="9.2837" x2="47.3583" y2="9.3599" layer="200"/>
<rectangle x1="50.4825" y1="9.2837" x2="51.4731" y2="9.3599" layer="200"/>
<rectangle x1="54.6735" y1="9.2837" x2="55.8165" y2="9.3599" layer="200"/>
<rectangle x1="59.7789" y1="9.2837" x2="60.8457" y2="9.3599" layer="200"/>
<rectangle x1="64.1985" y1="9.2837" x2="65.1891" y2="9.3599" layer="200"/>
<rectangle x1="68.4657" y1="9.2837" x2="69.6849" y2="9.3599" layer="200"/>
<rectangle x1="33.2613" y1="9.3599" x2="34.2519" y2="9.4361" layer="200"/>
<rectangle x1="37.2237" y1="9.3599" x2="38.2905" y2="9.4361" layer="200"/>
<rectangle x1="46.3677" y1="9.3599" x2="47.3583" y2="9.4361" layer="200"/>
<rectangle x1="50.4825" y1="9.3599" x2="51.4731" y2="9.4361" layer="200"/>
<rectangle x1="54.7497" y1="9.3599" x2="55.8165" y2="9.4361" layer="200"/>
<rectangle x1="59.7789" y1="9.3599" x2="60.8457" y2="9.4361" layer="200"/>
<rectangle x1="64.1985" y1="9.3599" x2="65.1891" y2="9.4361" layer="200"/>
<rectangle x1="68.3895" y1="9.3599" x2="69.6087" y2="9.4361" layer="200"/>
<rectangle x1="33.2613" y1="9.4361" x2="34.2519" y2="9.5123" layer="200"/>
<rectangle x1="37.2237" y1="9.4361" x2="38.2905" y2="9.5123" layer="200"/>
<rectangle x1="46.2915" y1="9.4361" x2="47.3583" y2="9.5123" layer="200"/>
<rectangle x1="50.4825" y1="9.4361" x2="51.4731" y2="9.5123" layer="200"/>
<rectangle x1="54.7497" y1="9.4361" x2="55.8165" y2="9.5123" layer="200"/>
<rectangle x1="59.7027" y1="9.4361" x2="60.8457" y2="9.5123" layer="200"/>
<rectangle x1="64.1985" y1="9.4361" x2="65.1891" y2="9.5123" layer="200"/>
<rectangle x1="68.3895" y1="9.4361" x2="69.5325" y2="9.5123" layer="200"/>
<rectangle x1="33.2613" y1="9.5123" x2="34.2519" y2="9.5885" layer="200"/>
<rectangle x1="37.2237" y1="9.5123" x2="38.2905" y2="9.5885" layer="200"/>
<rectangle x1="46.2915" y1="9.5123" x2="47.3583" y2="9.5885" layer="200"/>
<rectangle x1="50.4825" y1="9.5123" x2="51.4731" y2="9.5885" layer="200"/>
<rectangle x1="54.7497" y1="9.5123" x2="55.8927" y2="9.5885" layer="200"/>
<rectangle x1="59.7027" y1="9.5123" x2="60.8457" y2="9.5885" layer="200"/>
<rectangle x1="64.1985" y1="9.5123" x2="65.1891" y2="9.5885" layer="200"/>
<rectangle x1="68.3895" y1="9.5123" x2="69.4563" y2="9.5885" layer="200"/>
<rectangle x1="33.2613" y1="9.5885" x2="34.2519" y2="9.6647" layer="200"/>
<rectangle x1="37.2237" y1="9.5885" x2="38.2905" y2="9.6647" layer="200"/>
<rectangle x1="46.2915" y1="9.5885" x2="47.3583" y2="9.6647" layer="200"/>
<rectangle x1="50.4825" y1="9.5885" x2="51.4731" y2="9.6647" layer="200"/>
<rectangle x1="54.8259" y1="9.5885" x2="55.8927" y2="9.6647" layer="200"/>
<rectangle x1="59.7027" y1="9.5885" x2="60.7695" y2="9.6647" layer="200"/>
<rectangle x1="64.1985" y1="9.5885" x2="65.1891" y2="9.6647" layer="200"/>
<rectangle x1="68.3895" y1="9.5885" x2="69.4563" y2="9.6647" layer="200"/>
<rectangle x1="33.2613" y1="9.6647" x2="34.2519" y2="9.7409" layer="200"/>
<rectangle x1="37.2237" y1="9.6647" x2="38.2905" y2="9.7409" layer="200"/>
<rectangle x1="46.2915" y1="9.6647" x2="47.2821" y2="9.7409" layer="200"/>
<rectangle x1="50.4825" y1="9.6647" x2="51.4731" y2="9.7409" layer="200"/>
<rectangle x1="54.8259" y1="9.6647" x2="55.9689" y2="9.7409" layer="200"/>
<rectangle x1="59.6265" y1="9.6647" x2="60.7695" y2="9.7409" layer="200"/>
<rectangle x1="64.1985" y1="9.6647" x2="65.1891" y2="9.7409" layer="200"/>
<rectangle x1="68.3895" y1="9.6647" x2="69.3801" y2="9.7409" layer="200"/>
<rectangle x1="33.2613" y1="9.7409" x2="34.2519" y2="9.8171" layer="200"/>
<rectangle x1="37.2237" y1="9.7409" x2="38.2143" y2="9.8171" layer="200"/>
<rectangle x1="46.2915" y1="9.7409" x2="47.2821" y2="9.8171" layer="200"/>
<rectangle x1="50.4825" y1="9.7409" x2="51.4731" y2="9.8171" layer="200"/>
<rectangle x1="54.8259" y1="9.7409" x2="55.9689" y2="9.8171" layer="200"/>
<rectangle x1="59.6265" y1="9.7409" x2="60.7695" y2="9.8171" layer="200"/>
<rectangle x1="64.1985" y1="9.7409" x2="65.1891" y2="9.8171" layer="200"/>
<rectangle x1="68.3895" y1="9.7409" x2="69.3801" y2="9.8171" layer="200"/>
<rectangle x1="33.2613" y1="9.8171" x2="34.2519" y2="9.8933" layer="200"/>
<rectangle x1="37.2237" y1="9.8171" x2="38.2143" y2="9.8933" layer="200"/>
<rectangle x1="46.2153" y1="9.8171" x2="47.2821" y2="9.8933" layer="200"/>
<rectangle x1="50.4825" y1="9.8171" x2="51.4731" y2="9.8933" layer="200"/>
<rectangle x1="54.9021" y1="9.8171" x2="56.0451" y2="9.8933" layer="200"/>
<rectangle x1="59.5503" y1="9.8171" x2="60.6933" y2="9.8933" layer="200"/>
<rectangle x1="64.1985" y1="9.8171" x2="65.1891" y2="9.8933" layer="200"/>
<rectangle x1="68.3895" y1="9.8171" x2="69.3801" y2="9.8933" layer="200"/>
<rectangle x1="33.2613" y1="9.8933" x2="34.3281" y2="9.9695" layer="200"/>
<rectangle x1="37.2237" y1="9.8933" x2="38.2143" y2="9.9695" layer="200"/>
<rectangle x1="46.2153" y1="9.8933" x2="47.2821" y2="9.9695" layer="200"/>
<rectangle x1="50.4825" y1="9.8933" x2="51.4731" y2="9.9695" layer="200"/>
<rectangle x1="54.9021" y1="9.8933" x2="56.0451" y2="9.9695" layer="200"/>
<rectangle x1="59.5503" y1="9.8933" x2="60.6933" y2="9.9695" layer="200"/>
<rectangle x1="64.1985" y1="9.8933" x2="65.1891" y2="9.9695" layer="200"/>
<rectangle x1="68.3895" y1="9.8933" x2="69.3801" y2="9.9695" layer="200"/>
<rectangle x1="33.2613" y1="9.9695" x2="34.3281" y2="10.0457" layer="200"/>
<rectangle x1="37.2237" y1="9.9695" x2="38.2143" y2="10.0457" layer="200"/>
<rectangle x1="46.2153" y1="9.9695" x2="47.2821" y2="10.0457" layer="200"/>
<rectangle x1="50.4825" y1="9.9695" x2="51.4731" y2="10.0457" layer="200"/>
<rectangle x1="54.9783" y1="9.9695" x2="56.1213" y2="10.0457" layer="200"/>
<rectangle x1="59.4741" y1="9.9695" x2="60.6171" y2="10.0457" layer="200"/>
<rectangle x1="64.1985" y1="9.9695" x2="65.1891" y2="10.0457" layer="200"/>
<rectangle x1="68.3895" y1="9.9695" x2="69.3801" y2="10.0457" layer="200"/>
<rectangle x1="33.2613" y1="10.0457" x2="34.3281" y2="10.1219" layer="200"/>
<rectangle x1="37.1475" y1="10.0457" x2="38.2143" y2="10.1219" layer="200"/>
<rectangle x1="46.1391" y1="10.0457" x2="47.2821" y2="10.1219" layer="200"/>
<rectangle x1="50.4825" y1="10.0457" x2="51.4731" y2="10.1219" layer="200"/>
<rectangle x1="54.9783" y1="10.0457" x2="56.1213" y2="10.1219" layer="200"/>
<rectangle x1="59.4741" y1="10.0457" x2="60.6171" y2="10.1219" layer="200"/>
<rectangle x1="64.1985" y1="10.0457" x2="65.1891" y2="10.1219" layer="200"/>
<rectangle x1="68.3895" y1="10.0457" x2="69.3801" y2="10.1219" layer="200"/>
<rectangle x1="33.3375" y1="10.1219" x2="34.3281" y2="10.1981" layer="200"/>
<rectangle x1="37.1475" y1="10.1219" x2="38.2143" y2="10.1981" layer="200"/>
<rectangle x1="46.1391" y1="10.1219" x2="47.2821" y2="10.1981" layer="200"/>
<rectangle x1="50.4825" y1="10.1219" x2="51.4731" y2="10.1981" layer="200"/>
<rectangle x1="54.9783" y1="10.1219" x2="56.1975" y2="10.1981" layer="200"/>
<rectangle x1="59.3979" y1="10.1219" x2="60.5409" y2="10.1981" layer="200"/>
<rectangle x1="64.1985" y1="10.1219" x2="65.1891" y2="10.1981" layer="200"/>
<rectangle x1="68.3895" y1="10.1219" x2="69.3801" y2="10.1981" layer="200"/>
<rectangle x1="33.3375" y1="10.1981" x2="34.4043" y2="10.2743" layer="200"/>
<rectangle x1="37.1475" y1="10.1981" x2="38.1381" y2="10.2743" layer="200"/>
<rectangle x1="46.0629" y1="10.1981" x2="47.2059" y2="10.2743" layer="200"/>
<rectangle x1="50.4825" y1="10.1981" x2="51.4731" y2="10.2743" layer="200"/>
<rectangle x1="55.0545" y1="10.1981" x2="56.2737" y2="10.2743" layer="200"/>
<rectangle x1="59.3217" y1="10.1981" x2="60.5409" y2="10.2743" layer="200"/>
<rectangle x1="64.1985" y1="10.1981" x2="65.1891" y2="10.2743" layer="200"/>
<rectangle x1="68.3895" y1="10.1981" x2="69.3801" y2="10.2743" layer="200"/>
<rectangle x1="33.3375" y1="10.2743" x2="34.4043" y2="10.3505" layer="200"/>
<rectangle x1="37.0713" y1="10.2743" x2="38.1381" y2="10.3505" layer="200"/>
<rectangle x1="45.9867" y1="10.2743" x2="47.2059" y2="10.3505" layer="200"/>
<rectangle x1="50.4825" y1="10.2743" x2="51.4731" y2="10.3505" layer="200"/>
<rectangle x1="55.1307" y1="10.2743" x2="56.2737" y2="10.3505" layer="200"/>
<rectangle x1="59.3217" y1="10.2743" x2="60.4647" y2="10.3505" layer="200"/>
<rectangle x1="64.1985" y1="10.2743" x2="65.1891" y2="10.3505" layer="200"/>
<rectangle x1="68.3895" y1="10.2743" x2="69.4563" y2="10.3505" layer="200"/>
<rectangle x1="33.4137" y1="10.3505" x2="34.4805" y2="10.4267" layer="200"/>
<rectangle x1="37.0713" y1="10.3505" x2="38.1381" y2="10.4267" layer="200"/>
<rectangle x1="45.9867" y1="10.3505" x2="47.2059" y2="10.4267" layer="200"/>
<rectangle x1="50.4825" y1="10.3505" x2="51.4731" y2="10.4267" layer="200"/>
<rectangle x1="55.1307" y1="10.3505" x2="56.3499" y2="10.4267" layer="200"/>
<rectangle x1="59.2455" y1="10.3505" x2="60.4647" y2="10.4267" layer="200"/>
<rectangle x1="64.1985" y1="10.3505" x2="65.1891" y2="10.4267" layer="200"/>
<rectangle x1="68.3895" y1="10.3505" x2="69.4563" y2="10.4267" layer="200"/>
<rectangle x1="33.4137" y1="10.4267" x2="34.4805" y2="10.5029" layer="200"/>
<rectangle x1="36.9951" y1="10.4267" x2="38.0619" y2="10.5029" layer="200"/>
<rectangle x1="42.4815" y1="10.4267" x2="42.5577" y2="10.5029" layer="200"/>
<rectangle x1="45.9105" y1="10.4267" x2="47.1297" y2="10.5029" layer="200"/>
<rectangle x1="50.4825" y1="10.4267" x2="51.4731" y2="10.5029" layer="200"/>
<rectangle x1="55.2069" y1="10.4267" x2="56.4261" y2="10.5029" layer="200"/>
<rectangle x1="59.1693" y1="10.4267" x2="60.3885" y2="10.5029" layer="200"/>
<rectangle x1="64.1985" y1="10.4267" x2="65.1891" y2="10.5029" layer="200"/>
<rectangle x1="68.4657" y1="10.4267" x2="69.5325" y2="10.5029" layer="200"/>
<rectangle x1="33.4899" y1="10.5029" x2="34.5567" y2="10.5791" layer="200"/>
<rectangle x1="36.9951" y1="10.5029" x2="38.0619" y2="10.5791" layer="200"/>
<rectangle x1="42.4815" y1="10.5029" x2="42.7101" y2="10.5791" layer="200"/>
<rectangle x1="45.8343" y1="10.5029" x2="47.1297" y2="10.5791" layer="200"/>
<rectangle x1="50.4825" y1="10.5029" x2="51.4731" y2="10.5791" layer="200"/>
<rectangle x1="55.2069" y1="10.5029" x2="56.5023" y2="10.5791" layer="200"/>
<rectangle x1="59.0931" y1="10.5029" x2="60.3123" y2="10.5791" layer="200"/>
<rectangle x1="64.1985" y1="10.5029" x2="65.1891" y2="10.5791" layer="200"/>
<rectangle x1="68.4657" y1="10.5029" x2="69.6087" y2="10.5791" layer="200"/>
<rectangle x1="33.4899" y1="10.5791" x2="34.6329" y2="10.6553" layer="200"/>
<rectangle x1="36.9189" y1="10.5791" x2="37.9857" y2="10.6553" layer="200"/>
<rectangle x1="42.4815" y1="10.5791" x2="42.8625" y2="10.6553" layer="200"/>
<rectangle x1="45.7581" y1="10.5791" x2="47.1297" y2="10.6553" layer="200"/>
<rectangle x1="50.4825" y1="10.5791" x2="51.4731" y2="10.6553" layer="200"/>
<rectangle x1="55.2831" y1="10.5791" x2="56.6547" y2="10.6553" layer="200"/>
<rectangle x1="59.0169" y1="10.5791" x2="60.3123" y2="10.6553" layer="200"/>
<rectangle x1="64.1985" y1="10.5791" x2="65.1891" y2="10.6553" layer="200"/>
<rectangle x1="68.5419" y1="10.5791" x2="69.6849" y2="10.6553" layer="200"/>
<rectangle x1="33.5661" y1="10.6553" x2="34.6329" y2="10.7315" layer="200"/>
<rectangle x1="36.8427" y1="10.6553" x2="37.9095" y2="10.7315" layer="200"/>
<rectangle x1="42.4053" y1="10.6553" x2="43.0911" y2="10.7315" layer="200"/>
<rectangle x1="45.6057" y1="10.6553" x2="47.0535" y2="10.7315" layer="200"/>
<rectangle x1="50.4825" y1="10.6553" x2="51.4731" y2="10.7315" layer="200"/>
<rectangle x1="55.3593" y1="10.6553" x2="56.7309" y2="10.7315" layer="200"/>
<rectangle x1="58.8645" y1="10.6553" x2="60.2361" y2="10.7315" layer="200"/>
<rectangle x1="64.1985" y1="10.6553" x2="65.1891" y2="10.7315" layer="200"/>
<rectangle x1="68.5419" y1="10.6553" x2="69.7611" y2="10.7315" layer="200"/>
<rectangle x1="33.5661" y1="10.7315" x2="34.7091" y2="10.8077" layer="200"/>
<rectangle x1="36.7665" y1="10.7315" x2="37.9095" y2="10.8077" layer="200"/>
<rectangle x1="42.4053" y1="10.7315" x2="43.3197" y2="10.8077" layer="200"/>
<rectangle x1="45.5295" y1="10.7315" x2="47.0535" y2="10.8077" layer="200"/>
<rectangle x1="50.4825" y1="10.7315" x2="51.4731" y2="10.8077" layer="200"/>
<rectangle x1="55.4355" y1="10.7315" x2="56.8833" y2="10.8077" layer="200"/>
<rectangle x1="58.7883" y1="10.7315" x2="60.1599" y2="10.8077" layer="200"/>
<rectangle x1="64.1985" y1="10.7315" x2="65.1891" y2="10.8077" layer="200"/>
<rectangle x1="68.6181" y1="10.7315" x2="69.9135" y2="10.8077" layer="200"/>
<rectangle x1="33.6423" y1="10.8077" x2="34.8615" y2="10.8839" layer="200"/>
<rectangle x1="36.6903" y1="10.8077" x2="37.8333" y2="10.8839" layer="200"/>
<rectangle x1="42.3291" y1="10.8077" x2="43.5483" y2="10.8839" layer="200"/>
<rectangle x1="45.3771" y1="10.8077" x2="46.9773" y2="10.8839" layer="200"/>
<rectangle x1="50.4825" y1="10.8077" x2="51.4731" y2="10.8839" layer="200"/>
<rectangle x1="55.4355" y1="10.8077" x2="57.0357" y2="10.8839" layer="200"/>
<rectangle x1="58.5597" y1="10.8077" x2="60.0837" y2="10.8839" layer="200"/>
<rectangle x1="63.2841" y1="10.8077" x2="65.1891" y2="10.8839" layer="200"/>
<rectangle x1="68.6181" y1="10.8077" x2="69.9897" y2="10.8839" layer="200"/>
<rectangle x1="72.8091" y1="10.8077" x2="73.0377" y2="10.8839" layer="200"/>
<rectangle x1="33.7185" y1="10.8839" x2="34.9377" y2="10.9601" layer="200"/>
<rectangle x1="36.5379" y1="10.8839" x2="37.7571" y2="10.9601" layer="200"/>
<rectangle x1="38.9763" y1="10.8839" x2="39.2049" y2="10.9601" layer="200"/>
<rectangle x1="42.3291" y1="10.8839" x2="43.8531" y2="10.9601" layer="200"/>
<rectangle x1="45.1485" y1="10.8839" x2="46.9773" y2="10.9601" layer="200"/>
<rectangle x1="50.4825" y1="10.8839" x2="51.4731" y2="10.9601" layer="200"/>
<rectangle x1="55.5117" y1="10.8839" x2="57.1881" y2="10.9601" layer="200"/>
<rectangle x1="58.4073" y1="10.8839" x2="60.0837" y2="10.9601" layer="200"/>
<rectangle x1="63.2841" y1="10.8839" x2="65.1891" y2="10.9601" layer="200"/>
<rectangle x1="68.6943" y1="10.8839" x2="70.2183" y2="10.9601" layer="200"/>
<rectangle x1="72.5043" y1="10.8839" x2="73.0377" y2="10.9601" layer="200"/>
<rectangle x1="33.7947" y1="10.9601" x2="35.0901" y2="11.0363" layer="200"/>
<rectangle x1="36.4617" y1="10.9601" x2="37.6809" y2="11.0363" layer="200"/>
<rectangle x1="38.5191" y1="10.9601" x2="39.2049" y2="11.0363" layer="200"/>
<rectangle x1="42.2529" y1="10.9601" x2="46.9011" y2="11.0363" layer="200"/>
<rectangle x1="50.4825" y1="10.9601" x2="51.4731" y2="11.0363" layer="200"/>
<rectangle x1="55.5879" y1="10.9601" x2="60.0075" y2="11.0363" layer="200"/>
<rectangle x1="63.2841" y1="10.9601" x2="65.1891" y2="11.0363" layer="200"/>
<rectangle x1="68.7705" y1="10.9601" x2="70.4469" y2="11.0363" layer="200"/>
<rectangle x1="72.0471" y1="10.9601" x2="73.0377" y2="11.0363" layer="200"/>
<rectangle x1="33.8709" y1="11.0363" x2="35.2425" y2="11.1125" layer="200"/>
<rectangle x1="36.3093" y1="11.0363" x2="37.6047" y2="11.1125" layer="200"/>
<rectangle x1="38.0619" y1="11.0363" x2="39.2049" y2="11.1125" layer="200"/>
<rectangle x1="42.2529" y1="11.0363" x2="46.8249" y2="11.1125" layer="200"/>
<rectangle x1="50.4825" y1="11.0363" x2="51.4731" y2="11.1125" layer="200"/>
<rectangle x1="55.6641" y1="11.0363" x2="59.9313" y2="11.1125" layer="200"/>
<rectangle x1="63.2841" y1="11.0363" x2="65.1891" y2="11.1125" layer="200"/>
<rectangle x1="68.8467" y1="11.0363" x2="70.9803" y2="11.1125" layer="200"/>
<rectangle x1="71.5137" y1="11.0363" x2="73.0377" y2="11.1125" layer="200"/>
<rectangle x1="33.9471" y1="11.1125" x2="35.5473" y2="11.1887" layer="200"/>
<rectangle x1="36.0045" y1="11.1125" x2="39.2049" y2="11.1887" layer="200"/>
<rectangle x1="42.3291" y1="11.1125" x2="46.7487" y2="11.1887" layer="200"/>
<rectangle x1="50.4825" y1="11.1125" x2="51.4731" y2="11.1887" layer="200"/>
<rectangle x1="55.7403" y1="11.1125" x2="59.8551" y2="11.1887" layer="200"/>
<rectangle x1="63.2841" y1="11.1125" x2="65.1891" y2="11.1887" layer="200"/>
<rectangle x1="68.9229" y1="11.1125" x2="73.1139" y2="11.1887" layer="200"/>
<rectangle x1="34.0233" y1="11.1887" x2="39.2049" y2="11.2649" layer="200"/>
<rectangle x1="42.4815" y1="11.1887" x2="46.6725" y2="11.2649" layer="200"/>
<rectangle x1="50.4825" y1="11.1887" x2="51.4731" y2="11.2649" layer="200"/>
<rectangle x1="55.8927" y1="11.1887" x2="59.7027" y2="11.2649" layer="200"/>
<rectangle x1="63.2841" y1="11.1887" x2="65.1891" y2="11.2649" layer="200"/>
<rectangle x1="68.9991" y1="11.1887" x2="73.1139" y2="11.2649" layer="200"/>
<rectangle x1="34.0995" y1="11.2649" x2="39.2049" y2="11.3411" layer="200"/>
<rectangle x1="42.6339" y1="11.2649" x2="46.5963" y2="11.3411" layer="200"/>
<rectangle x1="50.4825" y1="11.2649" x2="51.4731" y2="11.3411" layer="200"/>
<rectangle x1="55.9689" y1="11.2649" x2="59.6265" y2="11.3411" layer="200"/>
<rectangle x1="63.2841" y1="11.2649" x2="65.1891" y2="11.3411" layer="200"/>
<rectangle x1="69.1515" y1="11.2649" x2="73.1139" y2="11.3411" layer="200"/>
<rectangle x1="34.1757" y1="11.3411" x2="39.2049" y2="11.4173" layer="200"/>
<rectangle x1="42.7863" y1="11.3411" x2="46.5201" y2="11.4173" layer="200"/>
<rectangle x1="50.4825" y1="11.3411" x2="51.4731" y2="11.4173" layer="200"/>
<rectangle x1="56.0451" y1="11.3411" x2="59.5503" y2="11.4173" layer="200"/>
<rectangle x1="63.2841" y1="11.3411" x2="65.1891" y2="11.4173" layer="200"/>
<rectangle x1="69.2277" y1="11.3411" x2="73.1139" y2="11.4173" layer="200"/>
<rectangle x1="34.3281" y1="11.4173" x2="39.2049" y2="11.4935" layer="200"/>
<rectangle x1="42.9387" y1="11.4173" x2="46.4439" y2="11.4935" layer="200"/>
<rectangle x1="50.4825" y1="11.4173" x2="51.4731" y2="11.4935" layer="200"/>
<rectangle x1="56.1975" y1="11.4173" x2="59.3979" y2="11.4935" layer="200"/>
<rectangle x1="63.2841" y1="11.4173" x2="65.1891" y2="11.4935" layer="200"/>
<rectangle x1="69.3801" y1="11.4173" x2="73.1901" y2="11.4935" layer="200"/>
<rectangle x1="34.4043" y1="11.4935" x2="39.2049" y2="11.5697" layer="200"/>
<rectangle x1="43.1673" y1="11.4935" x2="46.3677" y2="11.5697" layer="200"/>
<rectangle x1="50.4825" y1="11.4935" x2="51.4731" y2="11.5697" layer="200"/>
<rectangle x1="56.2737" y1="11.4935" x2="59.2455" y2="11.5697" layer="200"/>
<rectangle x1="63.2841" y1="11.4935" x2="65.1891" y2="11.5697" layer="200"/>
<rectangle x1="69.5325" y1="11.4935" x2="73.1901" y2="11.5697" layer="200"/>
<rectangle x1="34.5567" y1="11.5697" x2="36.9189" y2="11.6459" layer="200"/>
<rectangle x1="37.3761" y1="11.5697" x2="39.2049" y2="11.6459" layer="200"/>
<rectangle x1="43.3959" y1="11.5697" x2="46.2153" y2="11.6459" layer="200"/>
<rectangle x1="50.4825" y1="11.5697" x2="51.4731" y2="11.6459" layer="200"/>
<rectangle x1="56.5023" y1="11.5697" x2="59.0931" y2="11.6459" layer="200"/>
<rectangle x1="63.2841" y1="11.5697" x2="65.1891" y2="11.6459" layer="200"/>
<rectangle x1="69.6849" y1="11.5697" x2="73.1139" y2="11.6459" layer="200"/>
<rectangle x1="34.7091" y1="11.6459" x2="36.7665" y2="11.7221" layer="200"/>
<rectangle x1="37.9095" y1="11.6459" x2="39.2049" y2="11.7221" layer="200"/>
<rectangle x1="43.6245" y1="11.6459" x2="45.9867" y2="11.7221" layer="200"/>
<rectangle x1="50.4825" y1="11.6459" x2="51.4731" y2="11.7221" layer="200"/>
<rectangle x1="56.6547" y1="11.6459" x2="58.9407" y2="11.7221" layer="200"/>
<rectangle x1="63.2841" y1="11.6459" x2="65.1891" y2="11.7221" layer="200"/>
<rectangle x1="69.9135" y1="11.6459" x2="72.8091" y2="11.7221" layer="200"/>
<rectangle x1="34.9377" y1="11.7221" x2="36.5379" y2="11.7983" layer="200"/>
<rectangle x1="38.4429" y1="11.7221" x2="39.2049" y2="11.7983" layer="200"/>
<rectangle x1="43.9293" y1="11.7221" x2="45.7581" y2="11.7983" layer="200"/>
<rectangle x1="50.4825" y1="11.7221" x2="51.4731" y2="11.7983" layer="200"/>
<rectangle x1="56.8833" y1="11.7221" x2="58.7121" y2="11.7983" layer="200"/>
<rectangle x1="70.2183" y1="11.7221" x2="72.5043" y2="11.7983" layer="200"/>
<rectangle x1="35.2425" y1="11.7983" x2="36.2331" y2="11.8745" layer="200"/>
<rectangle x1="38.9763" y1="11.7983" x2="39.2049" y2="11.8745" layer="200"/>
<rectangle x1="44.3103" y1="11.7983" x2="45.4533" y2="11.8745" layer="200"/>
<rectangle x1="50.4825" y1="11.7983" x2="51.4731" y2="11.8745" layer="200"/>
<rectangle x1="57.2643" y1="11.7983" x2="58.3311" y2="11.8745" layer="200"/>
<rectangle x1="70.5993" y1="11.7983" x2="72.0471" y2="11.8745" layer="200"/>
<rectangle x1="50.4825" y1="11.8745" x2="51.4731" y2="11.9507" layer="200"/>
<rectangle x1="50.4825" y1="11.9507" x2="51.4731" y2="12.0269" layer="200"/>
<rectangle x1="50.4825" y1="12.0269" x2="51.4731" y2="12.1031" layer="200"/>
<rectangle x1="50.4825" y1="12.1031" x2="51.4731" y2="12.1793" layer="200"/>
<rectangle x1="50.4825" y1="12.1793" x2="51.4731" y2="12.2555" layer="200"/>
<rectangle x1="50.4825" y1="12.2555" x2="51.4731" y2="12.3317" layer="200"/>
<rectangle x1="50.4825" y1="12.3317" x2="51.4731" y2="12.4079" layer="200"/>
<rectangle x1="50.4825" y1="12.4079" x2="51.4731" y2="12.4841" layer="200"/>
<rectangle x1="50.4825" y1="12.4841" x2="51.4731" y2="12.5603" layer="200"/>
<rectangle x1="50.4825" y1="12.5603" x2="51.4731" y2="12.6365" layer="200"/>
<rectangle x1="50.4825" y1="12.6365" x2="51.4731" y2="12.7127" layer="200"/>
<rectangle x1="50.4825" y1="12.7127" x2="51.4731" y2="12.7889" layer="200"/>
<rectangle x1="50.4825" y1="12.7889" x2="51.4731" y2="12.8651" layer="200"/>
<rectangle x1="50.4825" y1="12.8651" x2="51.4731" y2="12.9413" layer="200"/>
<rectangle x1="50.4825" y1="12.9413" x2="51.4731" y2="13.0175" layer="200"/>
<rectangle x1="50.4825" y1="13.0175" x2="51.4731" y2="13.0937" layer="200"/>
<rectangle x1="50.4825" y1="13.0937" x2="51.4731" y2="13.1699" layer="200"/>
<rectangle x1="50.4825" y1="13.1699" x2="51.4731" y2="13.2461" layer="200"/>
<rectangle x1="64.4271" y1="13.1699" x2="64.9605" y2="13.2461" layer="200"/>
<rectangle x1="50.4825" y1="13.2461" x2="51.4731" y2="13.3223" layer="200"/>
<rectangle x1="64.2747" y1="13.2461" x2="65.0367" y2="13.3223" layer="200"/>
<rectangle x1="50.4825" y1="13.3223" x2="51.4731" y2="13.3985" layer="200"/>
<rectangle x1="64.1985" y1="13.3223" x2="65.1129" y2="13.3985" layer="200"/>
<rectangle x1="50.4825" y1="13.3985" x2="51.4731" y2="13.4747" layer="200"/>
<rectangle x1="64.1223" y1="13.3985" x2="65.1891" y2="13.4747" layer="200"/>
<rectangle x1="50.4825" y1="13.4747" x2="51.4731" y2="13.5509" layer="200"/>
<rectangle x1="64.1223" y1="13.4747" x2="65.2653" y2="13.5509" layer="200"/>
<rectangle x1="50.4825" y1="13.5509" x2="51.4731" y2="13.6271" layer="200"/>
<rectangle x1="64.0461" y1="13.5509" x2="65.2653" y2="13.6271" layer="200"/>
<rectangle x1="50.4825" y1="13.6271" x2="51.4731" y2="13.7033" layer="200"/>
<rectangle x1="64.0461" y1="13.6271" x2="65.2653" y2="13.7033" layer="200"/>
<rectangle x1="50.4825" y1="13.7033" x2="51.4731" y2="13.7795" layer="200"/>
<rectangle x1="64.0461" y1="13.7033" x2="65.3415" y2="13.7795" layer="200"/>
<rectangle x1="50.4825" y1="13.7795" x2="51.4731" y2="13.8557" layer="200"/>
<rectangle x1="64.0461" y1="13.7795" x2="65.3415" y2="13.8557" layer="200"/>
<rectangle x1="50.4825" y1="13.8557" x2="51.4731" y2="13.9319" layer="200"/>
<rectangle x1="64.0461" y1="13.8557" x2="65.3415" y2="13.9319" layer="200"/>
<rectangle x1="50.4825" y1="13.9319" x2="51.4731" y2="14.0081" layer="200"/>
<rectangle x1="64.0461" y1="13.9319" x2="65.2653" y2="14.0081" layer="200"/>
<rectangle x1="50.4825" y1="14.0081" x2="51.4731" y2="14.0843" layer="200"/>
<rectangle x1="64.0461" y1="14.0081" x2="65.2653" y2="14.0843" layer="200"/>
<rectangle x1="50.4825" y1="14.0843" x2="51.4731" y2="14.1605" layer="200"/>
<rectangle x1="64.1223" y1="14.0843" x2="65.2653" y2="14.1605" layer="200"/>
<rectangle x1="50.4825" y1="14.1605" x2="51.4731" y2="14.2367" layer="200"/>
<rectangle x1="64.1985" y1="14.1605" x2="65.1891" y2="14.2367" layer="200"/>
<rectangle x1="50.4825" y1="14.2367" x2="51.4731" y2="14.3129" layer="200"/>
<rectangle x1="64.1985" y1="14.2367" x2="65.1129" y2="14.3129" layer="200"/>
<rectangle x1="50.4825" y1="14.3129" x2="51.4731" y2="14.3891" layer="200"/>
<rectangle x1="64.3509" y1="14.3129" x2="65.0367" y2="14.3891" layer="200"/>
<rectangle x1="50.4825" y1="14.3891" x2="51.4731" y2="14.4653" layer="200"/>
<rectangle x1="64.5033" y1="14.3891" x2="64.8843" y2="14.4653" layer="200"/>
<rectangle x1="50.4825" y1="14.4653" x2="51.4731" y2="14.5415" layer="200"/>
<rectangle x1="50.4825" y1="14.5415" x2="51.4731" y2="14.6177" layer="200"/>
<rectangle x1="50.4825" y1="14.6177" x2="51.4731" y2="14.6939" layer="200"/>
<rectangle x1="50.4825" y1="14.6939" x2="51.4731" y2="14.7701" layer="200"/>
<rectangle x1="50.4825" y1="14.7701" x2="51.4731" y2="14.8463" layer="200"/>
<rectangle x1="50.4825" y1="14.8463" x2="51.4731" y2="14.9225" layer="200"/>
<rectangle x1="50.4825" y1="14.9225" x2="51.4731" y2="14.9987" layer="200"/>
<rectangle x1="50.4825" y1="14.9987" x2="51.4731" y2="15.0749" layer="200"/>
<rectangle x1="25.4" y1="1.27" x2="26.67" y2="15.24" layer="202"/>
<rectangle x1="80.01" y1="1.27" x2="81.28" y2="15.24" layer="202"/>
</symbol>
</symbols>
<devicesets>
<deviceset name="TITLE_BLOCK_GALOIS">
<gates>
<gate name="G$1" symbol="TITLE_BLOCK_GALOIS" x="0" y="0"/>
</gates>
<devices>
<device name="">
<technologies>
<technology name=""/>
</technologies>
</device>
</devices>
</deviceset>
</devicesets>
</library>
<library name="supply1" urn="urn:adsk.eagle:library:371">
<description>&lt;b&gt;Supply Symbols&lt;/b&gt;&lt;p&gt;
 GND, VCC, 0V, +5V, -5V, etc.&lt;p&gt;
 Please keep in mind, that these devices are necessary for the
 automatic wiring of the supply signals.&lt;p&gt;
 The pin name defined in the symbol is identical to the net which is to be wired automatically.&lt;p&gt;
 In this library the device names are the same as the pin names of the symbols, therefore the correct signal names appear next to the supply symbols in the schematic.&lt;p&gt;
 &lt;author&gt;Created by librarian@cadsoft.de&lt;/author&gt;</description>
<packages>
</packages>
<symbols>
<symbol name="GND" urn="urn:adsk.eagle:symbol:26925/1" library_version="1">
<wire x1="-1.905" y1="0" x2="1.905" y2="0" width="0.254" layer="94"/>
<text x="-2.54" y="-2.54" size="1.778" layer="96">&gt;VALUE</text>
<pin name="GND" x="0" y="2.54" visible="off" length="short" direction="sup" rot="R270"/>
</symbol>
</symbols>
<devicesets>
<deviceset name="GND" urn="urn:adsk.eagle:component:26954/1" prefix="GND" library_version="1">
<description>&lt;b&gt;SUPPLY SYMBOL&lt;/b&gt;</description>
<gates>
<gate name="1" symbol="GND" x="0" y="0"/>
</gates>
<devices>
<device name="">
<technologies>
<technology name=""/>
</technologies>
</device>
</devices>
</deviceset>
</devicesets>
</library>
<library name="USER_SMT_CHIP_STANDARD">
<packages>
<package name="EIA0402">
<description>EIA SIZE CODE 0402, KEMET, DENSITY LEVEL B</description>
<smd name="P$1" x="-0.45" y="0" dx="0.62" dy="0.62" layer="1" thermals="no"/>
<smd name="P$2" x="0.45" y="0" dx="0.62" dy="0.62" layer="1" thermals="no"/>
<rectangle x1="-0.95" y1="-0.5" x2="0.95" y2="0.5" layer="39"/>
<text x="-0.889" y="0.635" size="1.016" layer="25" font="vector">&gt;NAME</text>
<wire x1="-0.4445" y1="0.1905" x2="0.4445" y2="0.1905" width="0.127" layer="51"/>
<wire x1="0.4445" y1="0.1905" x2="0.4445" y2="-0.1905" width="0" layer="51"/>
<wire x1="0.4445" y1="-0.1905" x2="-0.4445" y2="-0.1905" width="0.127" layer="51"/>
<wire x1="-0.4445" y1="-0.1905" x2="-0.4445" y2="0.1905" width="0" layer="51"/>
<rectangle x1="-0.508" y1="-0.254" x2="-0.254" y2="0.254" layer="51"/>
<rectangle x1="0.254" y1="-0.254" x2="0.508" y2="0.254" layer="51"/>
<wire x1="-0.889" y1="0.4318" x2="0.889" y2="0.4318" width="0.1016" layer="21"/>
<wire x1="0.889" y1="0.4318" x2="0.889" y2="-0.4318" width="0.1016" layer="21"/>
<wire x1="0.889" y1="-0.4318" x2="-0.889" y2="-0.4318" width="0.1016" layer="21"/>
<wire x1="-0.889" y1="-0.4318" x2="-0.889" y2="0.4318" width="0.1016" layer="21"/>
</package>
<package name="EIA0603">
<description>EIA SIZE CODE 0603, KEMET, DENSITY LEVEL B</description>
<smd name="P$1" x="-0.8" y="0" dx="1" dy="0.95" layer="1" rot="R270" thermals="no"/>
<smd name="P$2" x="0.8" y="0" dx="1" dy="0.95" layer="1" rot="R270" thermals="no"/>
<rectangle x1="-1.55" y1="-0.75" x2="1.55" y2="0.75" layer="39"/>
<text x="-1.524" y="0.889" size="1.016" layer="25" font="vector">&gt;NAME</text>
<rectangle x1="-0.8255" y1="-0.4445" x2="-0.4445" y2="0.4445" layer="51"/>
<rectangle x1="0.4445" y1="-0.4445" x2="0.8255" y2="0.4445" layer="51"/>
<wire x1="-0.762" y1="0.381" x2="0.762" y2="0.381" width="0.127" layer="51"/>
<wire x1="0.762" y1="0.381" x2="0.762" y2="-0.381" width="0" layer="51"/>
<wire x1="0.762" y1="-0.381" x2="-0.762" y2="-0.381" width="0.127" layer="51"/>
<wire x1="-0.762" y1="-0.381" x2="-0.762" y2="0.381" width="0" layer="51"/>
<wire x1="-1.4732" y1="0.6858" x2="1.4732" y2="0.6858" width="0.1016" layer="21"/>
<wire x1="1.4732" y1="0.6858" x2="1.4732" y2="-0.6858" width="0.1016" layer="21"/>
<wire x1="1.4732" y1="-0.6858" x2="-1.4732" y2="-0.6858" width="0.1016" layer="21"/>
<wire x1="-1.4732" y1="-0.6858" x2="-1.4732" y2="0.6858" width="0.1016" layer="21"/>
</package>
<package name="EIA0805">
<description>EIA SIZE CODE 0805, KEMET, DENSITY LEVEL B</description>
<smd name="P$1" x="-0.9" y="0" dx="1.45" dy="1.15" layer="1" rot="R90" thermals="no"/>
<smd name="P$2" x="0.9" y="0" dx="1.45" dy="1.15" layer="1" rot="R90" thermals="no"/>
<rectangle x1="-1.75" y1="-1" x2="1.75" y2="1" layer="39"/>
<text x="-1.778" y="1.143" size="1.016" layer="25" font="vector">&gt;NAME</text>
<rectangle x1="-1.016" y1="-0.635" x2="-0.508" y2="0.635" layer="51"/>
<rectangle x1="0.508" y1="-0.635" x2="1.016" y2="0.635" layer="51"/>
<wire x1="-0.9525" y1="0.5715" x2="0.9525" y2="0.5715" width="0.127" layer="51"/>
<wire x1="0.9525" y1="0.5715" x2="0.9525" y2="-0.5715" width="0" layer="51"/>
<wire x1="0.9525" y1="-0.5715" x2="-0.9525" y2="-0.5715" width="0.127" layer="51"/>
<wire x1="-0.9525" y1="-0.5715" x2="-0.9525" y2="0.5715" width="0" layer="51"/>
<wire x1="-1.6764" y1="0.9398" x2="1.6764" y2="0.9398" width="0.1016" layer="21"/>
<wire x1="1.6764" y1="0.9398" x2="1.6764" y2="-0.9398" width="0.1016" layer="21"/>
<wire x1="1.6764" y1="-0.9398" x2="-1.6764" y2="-0.9398" width="0.1016" layer="21"/>
<wire x1="-1.6764" y1="-0.9398" x2="-1.6764" y2="0.9398" width="0.1016" layer="21"/>
</package>
<package name="EIA1206">
<description>EIA SIZE CODE 1206, KEMET, DENSITY LEVEL B</description>
<smd name="P$1" x="-1.5" y="0" dx="1.8" dy="1.15" layer="1" rot="R90" thermals="no"/>
<smd name="P$2" x="1.5" y="0" dx="1.8" dy="1.15" layer="1" rot="R90" thermals="no"/>
<rectangle x1="-2.35" y1="-1.15" x2="2.35" y2="1.15" layer="39"/>
<text x="-2.286" y="1.27" size="1.016" layer="25" font="vector">&gt;NAME</text>
<rectangle x1="-2.159" y1="-0.254" x2="-0.508" y2="0.254" layer="51" rot="R90"/>
<rectangle x1="0.508" y1="-0.254" x2="2.159" y2="0.254" layer="51" rot="R90"/>
<wire x1="-1.524" y1="0.762" x2="1.524" y2="0.762" width="0.127" layer="51"/>
<wire x1="1.524" y1="0.762" x2="1.524" y2="-0.762" width="0" layer="51"/>
<wire x1="1.524" y1="-0.762" x2="-1.524" y2="-0.762" width="0.127" layer="51"/>
<wire x1="-1.524" y1="-0.762" x2="-1.524" y2="0.762" width="0" layer="51"/>
<wire x1="-2.286" y1="1.0922" x2="2.286" y2="1.0922" width="0.1016" layer="21"/>
<wire x1="2.286" y1="1.0922" x2="2.286" y2="-1.0922" width="0.1016" layer="21"/>
<wire x1="2.286" y1="-1.0922" x2="-2.286" y2="-1.0922" width="0.1016" layer="21"/>
<wire x1="-2.286" y1="-1.0922" x2="-2.286" y2="1.0922" width="0.1016" layer="21"/>
</package>
<package name="EIA1210">
<description>EIA SIZE CODE 1210, KEMET, DENSITY LEVEL B</description>
<smd name="P$1" x="-1.50798125" y="-0.010396875" dx="2.7" dy="1.15" layer="1" rot="R90" thermals="no"/>
<smd name="P$2" x="1.484340625" y="0.003796875" dx="2.7" dy="1.15" layer="1" rot="R90" thermals="no"/>
<rectangle x1="-2.35" y1="-1.6" x2="2.35" y2="1.6" layer="39"/>
<text x="-2.286" y="1.651" size="1.016" layer="25" font="vector">&gt;NAME</text>
<rectangle x1="-1.5875" y1="-1.27" x2="-1.0795" y2="1.27" layer="51"/>
<rectangle x1="1.0795" y1="-1.27" x2="1.5875" y2="1.27" layer="51"/>
<wire x1="-1.524" y1="1.2065" x2="1.524" y2="1.2065" width="0.127" layer="51"/>
<wire x1="1.524" y1="1.2065" x2="1.524" y2="-1.2065" width="0" layer="51"/>
<wire x1="1.524" y1="-1.2065" x2="-1.524" y2="-1.2065" width="0.127" layer="51"/>
<wire x1="-1.524" y1="-1.2065" x2="-1.524" y2="1.2065" width="0" layer="51"/>
<wire x1="-2.286" y1="1.524" x2="2.286" y2="1.524" width="0.1016" layer="21"/>
<wire x1="2.286" y1="1.524" x2="2.286" y2="-1.524" width="0.1016" layer="21"/>
<wire x1="2.286" y1="-1.524" x2="-2.286" y2="-1.524" width="0.1016" layer="21"/>
<wire x1="-2.286" y1="-1.524" x2="-2.286" y2="1.524" width="0.1016" layer="21"/>
</package>
<package name="EIA1808">
<description>EIA SIZE CODE 1808, KEMET, DENSITY LEVEL B</description>
<smd name="P$1" x="-2.2" y="0" dx="2.2" dy="1.55" layer="1" rot="R90" thermals="no"/>
<smd name="P$2" x="2.2" y="0" dx="2.2" dy="1.55" layer="1" rot="R90" thermals="no"/>
<rectangle x1="-3.25" y1="-1.35" x2="3.25" y2="1.35" layer="39"/>
<text x="-3.175" y="1.524" size="1.016" layer="25" font="vector">&gt;NAME</text>
<rectangle x1="-2.3495" y1="-1.016" x2="-1.7145" y2="1.016" layer="51"/>
<rectangle x1="1.7145" y1="-1.016" x2="2.3495" y2="1.016" layer="51"/>
<wire x1="-2.286" y1="0.9525" x2="2.286" y2="0.9525" width="0.127" layer="51"/>
<wire x1="-2.286" y1="-0.9525" x2="2.286" y2="-0.9525" width="0.127" layer="51"/>
</package>
<package name="EIA1812">
<description>EIA SIZE CODE 1812, KEMET, DENSITY LEVEL B</description>
<smd name="P$1" x="-2.05" y="0" dx="3.5" dy="1.4" layer="1" rot="R90" thermals="no"/>
<smd name="P$2" x="2.05" y="0" dx="3.5" dy="1.4" layer="1" rot="R90" thermals="no"/>
<rectangle x1="-3" y1="-2" x2="3" y2="2" layer="39"/>
<text x="-2.921" y="2.159" size="1.016" layer="25" font="vector">&gt;NAME</text>
<rectangle x1="-2.286" y1="-1.5875" x2="-1.651" y2="1.5875" layer="51"/>
<rectangle x1="1.651" y1="-1.5875" x2="2.286" y2="1.5875" layer="51"/>
<wire x1="-2.2225" y1="1.524" x2="2.2225" y2="1.524" width="0.127" layer="51"/>
<wire x1="-2.2225" y1="-1.524" x2="2.2225" y2="-1.524" width="0.127" layer="51"/>
</package>
<package name="EIA1825">
<description>EIA SIZE CODE 1825, KEMET, DENSITY LEVEL B</description>
<smd name="P$1" x="-2.05" y="0" dx="6.8" dy="1.4" layer="1" rot="R90" thermals="no"/>
<smd name="P$2" x="2.05" y="0" dx="6.8" dy="1.4" layer="1" rot="R90" thermals="no"/>
<rectangle x1="-3" y1="-3.65" x2="3" y2="3.65" layer="39"/>
<text x="-2.921" y="3.81" size="1.016" layer="25" font="vector">&gt;NAME</text>
<rectangle x1="-2.286" y1="-3.175" x2="-1.651" y2="3.175" layer="51"/>
<rectangle x1="1.651" y1="-3.175" x2="2.286" y2="3.175" layer="51"/>
<wire x1="-2.2225" y1="-3.1115" x2="2.2225" y2="-3.1115" width="0.127" layer="51"/>
<wire x1="-2.2225" y1="3.1115" x2="2.2225" y2="3.1115" width="0.127" layer="51"/>
</package>
<package name="EIA2220">
<description>EIA SIZE CODE 2220, KEMET, DENSITY LEVEL B</description>
<smd name="P$1" x="-2.65" y="0" dx="5.4" dy="1.5" layer="1" rot="R90" thermals="no"/>
<smd name="P$2" x="2.65" y="0" dx="5.4" dy="1.5" layer="1" rot="R90" thermals="no"/>
<rectangle x1="-3.65" y1="-2.95" x2="3.65" y2="2.95" layer="39"/>
<text x="-3.556" y="3.048" size="1.016" layer="25" font="vector">&gt;NAME</text>
<rectangle x1="-2.8575" y1="-2.54" x2="-2.2225" y2="2.54" layer="51"/>
<rectangle x1="2.2225" y1="-2.54" x2="2.8575" y2="2.54" layer="51"/>
<wire x1="-2.794" y1="2.4765" x2="2.794" y2="2.4765" width="0.127" layer="51"/>
<wire x1="-2.794" y1="-2.4765" x2="2.794" y2="-2.4765" width="0.127" layer="51"/>
</package>
<package name="EIA2225">
<description>EIA SIZE CODE 2225, KEMET, DENSITY LEVEL B</description>
<smd name="P$1" x="-2.6" y="0" dx="6.8" dy="1.5" layer="1" rot="R90" thermals="no"/>
<smd name="P$2" x="2.6" y="0" dx="6.8" dy="1.5" layer="1" rot="R90" thermals="no"/>
<rectangle x1="-3.6" y1="-3.65" x2="3.6" y2="3.65" layer="39"/>
<text x="-3.556" y="3.81" size="1.016" layer="25" font="vector">&gt;NAME</text>
<rectangle x1="-2.794" y1="-3.175" x2="-2.159" y2="3.175" layer="51"/>
<rectangle x1="2.159" y1="-3.175" x2="2.794" y2="3.175" layer="51"/>
<wire x1="-2.7305" y1="3.1115" x2="2.7305" y2="3.1115" width="0.127" layer="51"/>
<wire x1="2.7305" y1="3.1115" x2="2.7305" y2="3.048" width="0.127" layer="51"/>
<wire x1="-2.7305" y1="-3.1115" x2="2.7305" y2="-3.1115" width="0.127" layer="51"/>
</package>
<package name="EIA2512">
<smd name="P$1" x="-2.825" y="0" dx="2.7" dy="3.6" layer="1" rot="R180"/>
<smd name="P$2" x="2.825" y="0" dx="2.7" dy="3.6" layer="1" rot="R180"/>
<wire x1="-4.5" y1="2.25" x2="4.5" y2="2.25" width="0.127" layer="21"/>
<wire x1="4.5" y1="2.25" x2="4.5" y2="-2.25" width="0.127" layer="21"/>
<wire x1="4.5" y1="-2.25" x2="-4.5" y2="-2.25" width="0.127" layer="21"/>
<wire x1="-4.5" y1="-2.25" x2="-4.5" y2="2.25" width="0.127" layer="21"/>
<text x="0" y="2.75" size="1" layer="21" font="vector" align="bottom-center">&gt;NAME</text>
</package>
<package name="EIA0603_LED">
<smd name="A" x="-0.8" y="0" dx="1" dy="0.95" layer="1" rot="R270" thermals="no"/>
<smd name="C" x="0.8" y="0" dx="1" dy="0.95" layer="1" rot="R270" thermals="no"/>
<rectangle x1="-1.55" y1="-0.75" x2="1.55" y2="0.75" layer="39"/>
<text x="-1.524" y="0.889" size="1.016" layer="25" font="vector">&gt;NAME</text>
<rectangle x1="-0.8255" y1="-0.4445" x2="-0.4445" y2="0.4445" layer="51"/>
<rectangle x1="0.4445" y1="-0.4445" x2="0.8255" y2="0.4445" layer="51"/>
<wire x1="-0.762" y1="0.381" x2="0.762" y2="0.381" width="0.127" layer="51"/>
<wire x1="0.762" y1="0.381" x2="0.762" y2="-0.381" width="0" layer="51"/>
<wire x1="0.762" y1="-0.381" x2="-0.762" y2="-0.381" width="0.127" layer="51"/>
<wire x1="-0.762" y1="-0.381" x2="-0.762" y2="0.381" width="0" layer="51"/>
<wire x1="-1.4732" y1="0.6858" x2="1.4732" y2="0.6858" width="0.1016" layer="21"/>
<wire x1="1.4732" y1="0.6858" x2="1.4732" y2="-0.6858" width="0.1016" layer="21"/>
<wire x1="1.4732" y1="-0.6858" x2="-1.4732" y2="-0.6858" width="0.1016" layer="21"/>
<wire x1="-1.4732" y1="-0.6858" x2="-1.4732" y2="0.6858" width="0.1016" layer="21"/>
<rectangle x1="1.778" y1="-0.762" x2="2.032" y2="0.762" layer="21"/>
</package>
</packages>
<symbols>
<symbol name="R">
<pin name="P$1" x="-2.54" y="0" visible="off" length="point" direction="pas"/>
<pin name="P$2" x="3.81" y="0" visible="off" length="point" direction="pas" rot="R180"/>
<text x="-1.27" y="2.54" size="1.27" layer="95" font="vector">&gt;NAME</text>
<text x="-1.27" y="-3.81" size="1.27" layer="96" font="vector">&gt;VALUE</text>
<wire x1="-1.27" y1="0" x2="-0.9525" y2="0.635" width="0.254" layer="94"/>
<wire x1="1.5875" y1="0.635" x2="0.9525" y2="-0.635" width="0.254" layer="94"/>
<wire x1="0.9525" y1="-0.635" x2="0.3175" y2="0.635" width="0.254" layer="94"/>
<wire x1="0.3175" y1="0.635" x2="-0.3175" y2="-0.635" width="0.254" layer="94"/>
<wire x1="-0.3175" y1="-0.635" x2="-0.9525" y2="0.635" width="0.254" layer="94"/>
<wire x1="1.5875" y1="0.635" x2="2.2225" y2="-0.635" width="0.254" layer="94"/>
<wire x1="2.2225" y1="-0.635" x2="2.54" y2="0" width="0.254" layer="94"/>
<wire x1="-2.54" y1="0" x2="-1.27" y2="0" width="0.254" layer="94"/>
<wire x1="2.54" y1="0" x2="3.81" y2="0" width="0.254" layer="94"/>
</symbol>
<symbol name="C">
<pin name="P$1" x="-2.54" y="0" visible="off" length="short" direction="pas"/>
<pin name="P$2" x="3.81" y="0" visible="off" length="short" direction="pas" rot="R180"/>
<wire x1="0" y1="1.27" x2="0" y2="-1.27" width="0.254" layer="94"/>
<wire x1="1.27" y1="1.27" x2="1.27" y2="-1.27" width="0.254" layer="94"/>
<text x="-1.27" y="2.54" size="1.27" layer="95" font="vector">&gt;NAME</text>
<text x="-1.27" y="-3.81" size="1.27" layer="96" font="vector">&gt;VALUE</text>
<text x="-1.27" y="-6.35" size="1.27" layer="97" font="vector">&gt;PACKAGE</text>
</symbol>
<symbol name="LED">
<pin name="A" x="-3.81" y="0" visible="off" length="short" direction="pas"/>
<pin name="C" x="3.81" y="0" visible="off" length="short" direction="pas" rot="R180"/>
<text x="-2.54" y="3.81" size="1.27" layer="95" font="vector">&gt;NAME</text>
<text x="-2.54" y="-3.81" size="1.27" layer="96" font="vector">&gt;VALUE</text>
<wire x1="1.27" y1="0" x2="-1.27" y2="1.27" width="0.254" layer="94"/>
<wire x1="-1.27" y1="1.27" x2="-1.27" y2="-1.27" width="0.254" layer="94"/>
<wire x1="-1.27" y1="-1.27" x2="1.27" y2="0" width="0.254" layer="94"/>
<wire x1="1.27" y1="1.27" x2="1.27" y2="-1.27" width="0.254" layer="94"/>
<wire x1="-0.9525" y1="1.905" x2="-0.635" y2="2.54" width="0.254" layer="94"/>
<wire x1="-0.635" y1="2.54" x2="-0.3175" y2="2.2225" width="0.254" layer="94"/>
<wire x1="-0.3175" y1="2.2225" x2="0.3175" y2="3.175" width="0.254" layer="94"/>
<wire x1="-0.3175" y1="1.27" x2="0" y2="1.905" width="0.254" layer="94"/>
<wire x1="0" y1="1.905" x2="0.3175" y2="1.5875" width="0.254" layer="94"/>
<wire x1="0.3175" y1="1.5875" x2="0.9525" y2="2.54" width="0.254" layer="94"/>
<wire x1="0.3175" y1="3.175" x2="-0.3175" y2="2.8575" width="0.254" layer="94"/>
<wire x1="0.3175" y1="3.175" x2="0.3175" y2="2.54" width="0.254" layer="94"/>
<wire x1="0.9525" y1="2.54" x2="0.3175" y2="2.2225" width="0.254" layer="94"/>
<wire x1="0.9525" y1="2.54" x2="0.9525" y2="1.905" width="0.254" layer="94"/>
</symbol>
</symbols>
<devicesets>
<deviceset name="R_SMD" prefix="R" uservalue="yes">
<gates>
<gate name="G$1" symbol="R" x="-5.08" y="0"/>
</gates>
<devices>
<device name="R0402" package="EIA0402">
<connects>
<connect gate="G$1" pin="P$1" pad="P$1"/>
<connect gate="G$1" pin="P$2" pad="P$2"/>
</connects>
<technologies>
<technology name="">
<attribute name="MPN" value="" constant="no"/>
</technology>
</technologies>
</device>
<device name="R0603" package="EIA0603">
<connects>
<connect gate="G$1" pin="P$1" pad="P$1"/>
<connect gate="G$1" pin="P$2" pad="P$2"/>
</connects>
<technologies>
<technology name="">
<attribute name="MPN" value="" constant="no"/>
<attribute name="PACKAGE" value="0603"/>
</technology>
</technologies>
</device>
<device name="R0805" package="EIA0805">
<connects>
<connect gate="G$1" pin="P$1" pad="P$1"/>
<connect gate="G$1" pin="P$2" pad="P$2"/>
</connects>
<technologies>
<technology name="">
<attribute name="MPN" value="" constant="no"/>
<attribute name="PACKAGE" value="0805"/>
</technology>
</technologies>
</device>
<device name="R1206" package="EIA1206">
<connects>
<connect gate="G$1" pin="P$1" pad="P$1"/>
<connect gate="G$1" pin="P$2" pad="P$2"/>
</connects>
<technologies>
<technology name="">
<attribute name="MPN" value="" constant="no"/>
<attribute name="PACKAGE" value="1206"/>
</technology>
</technologies>
</device>
<device name="R1210" package="EIA1210">
<connects>
<connect gate="G$1" pin="P$1" pad="P$1"/>
<connect gate="G$1" pin="P$2" pad="P$2"/>
</connects>
<technologies>
<technology name="">
<attribute name="MPN" value="" constant="no"/>
</technology>
</technologies>
</device>
<device name="R1808" package="EIA1808">
<connects>
<connect gate="G$1" pin="P$1" pad="P$1"/>
<connect gate="G$1" pin="P$2" pad="P$2"/>
</connects>
<technologies>
<technology name="">
<attribute name="MPN" value="" constant="no"/>
</technology>
</technologies>
</device>
<device name="R1812" package="EIA1812">
<connects>
<connect gate="G$1" pin="P$1" pad="P$1"/>
<connect gate="G$1" pin="P$2" pad="P$2"/>
</connects>
<technologies>
<technology name="">
<attribute name="MPN" value="" constant="no"/>
</technology>
</technologies>
</device>
<device name="R1825" package="EIA1825">
<connects>
<connect gate="G$1" pin="P$1" pad="P$1"/>
<connect gate="G$1" pin="P$2" pad="P$2"/>
</connects>
<technologies>
<technology name="">
<attribute name="MPN" value="" constant="no"/>
</technology>
</technologies>
</device>
<device name="R2220" package="EIA2220">
<connects>
<connect gate="G$1" pin="P$1" pad="P$1"/>
<connect gate="G$1" pin="P$2" pad="P$2"/>
</connects>
<technologies>
<technology name="">
<attribute name="MPN" value="" constant="no"/>
</technology>
</technologies>
</device>
<device name="R2225" package="EIA2225">
<connects>
<connect gate="G$1" pin="P$1" pad="P$1"/>
<connect gate="G$1" pin="P$2" pad="P$2"/>
</connects>
<technologies>
<technology name="">
<attribute name="MPN" value="" constant="no"/>
</technology>
</technologies>
</device>
<device name="R2512" package="EIA2512">
<connects>
<connect gate="G$1" pin="P$1" pad="P$1"/>
<connect gate="G$1" pin="P$2" pad="P$2"/>
</connects>
<technologies>
<technology name="">
<attribute name="MPN" value="" constant="no"/>
</technology>
</technologies>
</device>
</devices>
</deviceset>
<deviceset name="C_SMD" prefix="C" uservalue="yes">
<gates>
<gate name="G$1" symbol="C" x="0" y="0"/>
</gates>
<devices>
<device name="C0402" package="EIA0402">
<connects>
<connect gate="G$1" pin="P$1" pad="P$1"/>
<connect gate="G$1" pin="P$2" pad="P$2"/>
</connects>
<technologies>
<technology name="">
<attribute name="MPN" value="" constant="no"/>
<attribute name="PACKAGE" value="0402"/>
</technology>
</technologies>
</device>
<device name="C0603" package="EIA0603">
<connects>
<connect gate="G$1" pin="P$1" pad="P$1"/>
<connect gate="G$1" pin="P$2" pad="P$2"/>
</connects>
<technologies>
<technology name="">
<attribute name="MPN" value="" constant="no"/>
<attribute name="PACKAGE" value="0603"/>
</technology>
</technologies>
</device>
<device name="C0805" package="EIA0805">
<connects>
<connect gate="G$1" pin="P$1" pad="P$1"/>
<connect gate="G$1" pin="P$2" pad="P$2"/>
</connects>
<technologies>
<technology name="">
<attribute name="MPN" value="" constant="no"/>
<attribute name="PACKAGE" value="0805"/>
</technology>
</technologies>
</device>
<device name="C1206" package="EIA1206">
<connects>
<connect gate="G$1" pin="P$1" pad="P$1"/>
<connect gate="G$1" pin="P$2" pad="P$2"/>
</connects>
<technologies>
<technology name="">
<attribute name="MPN" value="" constant="no"/>
<attribute name="PACKAGE" value="1206"/>
</technology>
</technologies>
</device>
<device name="C1210" package="EIA1210">
<connects>
<connect gate="G$1" pin="P$1" pad="P$1"/>
<connect gate="G$1" pin="P$2" pad="P$2"/>
</connects>
<technologies>
<technology name="">
<attribute name="MPN" value="" constant="no"/>
<attribute name="PACKAGE" value="1210"/>
</technology>
</technologies>
</device>
<device name="C1808" package="EIA1808">
<connects>
<connect gate="G$1" pin="P$1" pad="P$1"/>
<connect gate="G$1" pin="P$2" pad="P$2"/>
</connects>
<technologies>
<technology name="">
<attribute name="MPN" value="" constant="no"/>
<attribute name="PACKAGE" value="1808"/>
</technology>
</technologies>
</device>
<device name="C1812" package="EIA1812">
<connects>
<connect gate="G$1" pin="P$1" pad="P$1"/>
<connect gate="G$1" pin="P$2" pad="P$2"/>
</connects>
<technologies>
<technology name="">
<attribute name="MPN" value="" constant="no"/>
<attribute name="PACKAGE" value="1812"/>
</technology>
</technologies>
</device>
<device name="C1825" package="EIA1825">
<connects>
<connect gate="G$1" pin="P$1" pad="P$1"/>
<connect gate="G$1" pin="P$2" pad="P$2"/>
</connects>
<technologies>
<technology name="">
<attribute name="MPN" value="" constant="no"/>
<attribute name="PACKAGE" value="1825"/>
</technology>
</technologies>
</device>
<device name="C2220" package="EIA2220">
<connects>
<connect gate="G$1" pin="P$1" pad="P$1"/>
<connect gate="G$1" pin="P$2" pad="P$2"/>
</connects>
<technologies>
<technology name="">
<attribute name="MPN" value="" constant="no"/>
<attribute name="PACKAGE" value="2220"/>
</technology>
</technologies>
</device>
<device name="C2225" package="EIA2225">
<connects>
<connect gate="G$1" pin="P$1" pad="P$1"/>
<connect gate="G$1" pin="P$2" pad="P$2"/>
</connects>
<technologies>
<technology name="">
<attribute name="MPN" value="" constant="no"/>
<attribute name="PACKAGE" value="2225"/>
</technology>
</technologies>
</device>
</devices>
</deviceset>
<deviceset name="LED_SMD" prefix="D" uservalue="yes">
<gates>
<gate name="G$1" symbol="LED" x="0" y="0"/>
</gates>
<devices>
<device name="" package="EIA0603_LED">
<connects>
<connect gate="G$1" pin="A" pad="A"/>
<connect gate="G$1" pin="C" pad="C"/>
</connects>
<technologies>
<technology name="">
<attribute name="MPN" value="" constant="no"/>
</technology>
</technologies>
</device>
</devices>
</deviceset>
</devicesets>
</library>
<library name="USER_CON_HIGH_CURRENT">
<packages>
<package name="FASTON_MALE_SERIES_250_THRU_R/A">
<pad name="1" x="-2.54" y="0" drill="1.524" diameter="2.54"/>
<pad name="2" x="2.54" y="0" drill="1.524" diameter="2.54"/>
<wire x1="-2.54" y1="0" x2="15.24" y2="0" width="0.8128" layer="51"/>
<text x="-5" y="0" size="1" layer="25" font="vector" rot="R180" align="center-left">&gt;NAME</text>
</package>
<package name="HPM_1X3_R/A">
<pad name="1" x="-5.08" y="0" drill="1.5748" diameter="3.175" shape="square"/>
<pad name="2" x="0" y="0" drill="1.5748" diameter="3.175"/>
<pad name="3" x="5.08" y="0" drill="1.5748" diameter="3.175"/>
<wire x1="-7.62" y1="2.54" x2="7.62" y2="2.54" width="0.127" layer="21"/>
<wire x1="7.62" y1="2.54" x2="7.62" y2="-2.54" width="0.127" layer="21"/>
<wire x1="7.62" y1="-2.54" x2="-7.62" y2="-2.54" width="0.127" layer="21"/>
<wire x1="-7.62" y1="-2.54" x2="-7.62" y2="2.54" width="0.127" layer="21"/>
<text x="-8.89" y="-2.54" size="1.016" layer="25" font="vector" rot="R90">&gt;NAME</text>
<wire x1="-5.08" y1="0" x2="-5.08" y2="-10.6172" width="1.143" layer="25"/>
<wire x1="0" y1="0" x2="0" y2="-10.6172" width="1.143" layer="25"/>
<wire x1="5.08" y1="0" x2="5.08" y2="-10.6172" width="1.143" layer="25"/>
</package>
</packages>
<symbols>
<symbol name="FASTON_MALE_PCB_R/A">
<wire x1="-2.54" y1="2.54" x2="-2.54" y2="-2.54" width="0.254" layer="94"/>
<wire x1="-2.54" y1="-2.54" x2="2.54" y2="-2.54" width="0.254" layer="94"/>
<wire x1="2.54" y1="-2.54" x2="2.54" y2="-1.27" width="0.254" layer="94"/>
<wire x1="2.54" y1="-1.27" x2="6.35" y2="-1.27" width="0.254" layer="94"/>
<wire x1="6.35" y1="-1.27" x2="6.35" y2="0" width="0.254" layer="94"/>
<wire x1="6.35" y1="0" x2="10.16" y2="0" width="0.254" layer="94"/>
<wire x1="10.16" y1="0" x2="10.795" y2="0.635" width="0.254" layer="94"/>
<wire x1="10.795" y1="0.635" x2="10.795" y2="1.905" width="0.254" layer="94"/>
<wire x1="10.795" y1="1.905" x2="10.16" y2="2.54" width="0.254" layer="94"/>
<wire x1="10.16" y1="2.54" x2="-2.54" y2="2.54" width="0.254" layer="94"/>
<circle x="8.5725" y="1.27" radius="0.3175" width="0.254" layer="94"/>
<pin name="1" x="-2.54" y="-5.08" visible="off" length="short" rot="R90"/>
<pin name="2" x="2.54" y="-5.08" visible="off" length="short" rot="R90"/>
<text x="-2.54" y="6.35" size="1.27" layer="95" font="vector">&gt;NAME</text>
<text x="-2.54" y="3.81" size="1.27" layer="96" font="vector">&gt;VALUE</text>
</symbol>
<symbol name="HPM_1X3">
<pin name="1" x="-7.62" y="5.08" visible="pin" length="middle"/>
<pin name="2" x="-7.62" y="0" visible="pin" length="middle"/>
<pin name="3" x="-7.62" y="-5.08" visible="pin" length="middle"/>
<wire x1="-2.54" y1="7.62" x2="-2.54" y2="-7.62" width="0.254" layer="94"/>
<wire x1="-2.54" y1="-7.62" x2="2.54" y2="-7.62" width="0.254" layer="94"/>
<wire x1="2.54" y1="-7.62" x2="2.54" y2="7.62" width="0.254" layer="94"/>
<wire x1="2.54" y1="7.62" x2="-2.54" y2="7.62" width="0.254" layer="94"/>
<text x="-2.54" y="8.89" size="1.27" layer="95" font="vector">&gt;NAME</text>
<text x="-2.54" y="-10.16" size="1.27" layer="96" font="vector">&gt;VALUE</text>
</symbol>
</symbols>
<devicesets>
<deviceset name="FASTON_PCB_THRU_R/A" prefix="J" uservalue="yes">
<gates>
<gate name="G$1" symbol="FASTON_MALE_PCB_R/A" x="0" y="0"/>
</gates>
<devices>
<device name="" package="FASTON_MALE_SERIES_250_THRU_R/A">
<connects>
<connect gate="G$1" pin="1" pad="1"/>
<connect gate="G$1" pin="2" pad="2"/>
</connects>
<technologies>
<technology name="">
<attribute name="MPN" value="" constant="no"/>
</technology>
</technologies>
</device>
</devices>
</deviceset>
<deviceset name="HPM_1X3_R/A" prefix="J" uservalue="yes">
<gates>
<gate name="G$1" symbol="HPM_1X3" x="0" y="0"/>
</gates>
<devices>
<device name="" package="HPM_1X3_R/A">
<connects>
<connect gate="G$1" pin="1" pad="1"/>
<connect gate="G$1" pin="2" pad="2"/>
<connect gate="G$1" pin="3" pad="3"/>
</connects>
<technologies>
<technology name="">
<attribute name="MPN" value="" constant="no"/>
</technology>
</technologies>
</device>
</devices>
</deviceset>
</devicesets>
</library>
<library name="USER_SMART_SWITCHES">
<packages>
<package name="PG-TO252-5-11">
<wire x1="2.68" y1="0.04" x2="2.68" y2="-0.09" width="0" layer="51"/>
<smd name="1" x="-2.28" y="0" dx="2.2" dy="0.8" layer="1" rot="R90"/>
<smd name="5" x="2.28" y="0" dx="2.2" dy="0.8" layer="1" rot="R90"/>
<smd name="4" x="1.14" y="0" dx="2.2" dy="0.8" layer="1" rot="R90"/>
<smd name="2" x="-1.14" y="0" dx="2.2" dy="0.8" layer="1" rot="R90"/>
<smd name="TAB" x="0" y="6.3" dx="5.8" dy="6.4" layer="1"/>
<wire x1="-3.25" y1="1.97" x2="3.25" y2="1.97" width="0.127" layer="51"/>
<wire x1="3.25" y1="1.97" x2="3.25" y2="8.19" width="0.127" layer="51"/>
<wire x1="3.25" y1="8.19" x2="-3.25" y2="8.19" width="0.127" layer="51"/>
<wire x1="-3.25" y1="8.19" x2="-3.25" y2="1.97" width="0.127" layer="51"/>
<rectangle x1="-2.85" y1="8.19" x2="2.85" y2="9.19" layer="51"/>
<rectangle x1="-2.58" y1="-0.79" x2="-1.98" y2="1.97" layer="51"/>
<rectangle x1="-1.44" y1="-0.79" x2="-0.84" y2="1.97" layer="51"/>
<rectangle x1="1.99" y1="-0.79" x2="2.59" y2="1.97" layer="51"/>
<rectangle x1="0.85" y1="-0.79" x2="1.45" y2="1.97" layer="51"/>
<text x="-3.75" y="2" size="1" layer="25" font="vector" rot="R90">&gt;NAME</text>
<wire x1="-3.25" y1="8.5" x2="-3.5" y2="8.25" width="0.127" layer="21"/>
<wire x1="-3.5" y1="8.25" x2="-3.5" y2="1.75" width="0.127" layer="21"/>
<wire x1="-3.5" y1="1.75" x2="3.5" y2="1.75" width="0.127" layer="21"/>
<wire x1="3.5" y1="1.75" x2="3.5" y2="8.25" width="0.127" layer="21"/>
<wire x1="3.5" y1="8.25" x2="3.25" y2="8.5" width="0.127" layer="21"/>
</package>
</packages>
<symbols>
<symbol name="ITS428L2">
<pin name="IN" x="-15.24" y="5.08" length="middle"/>
<pin name="ST" x="-15.24" y="-5.08" length="middle"/>
<pin name="VBB" x="15.24" y="5.08" length="middle" rot="R180"/>
<pin name="VOUT" x="15.24" y="-5.08" length="middle" rot="R180"/>
<wire x1="-10.16" y1="7.62" x2="-10.16" y2="-7.62" width="0.254" layer="94"/>
<wire x1="-10.16" y1="-7.62" x2="10.16" y2="-7.62" width="0.254" layer="94"/>
<wire x1="10.16" y1="-7.62" x2="10.16" y2="7.62" width="0.254" layer="94"/>
<wire x1="10.16" y1="7.62" x2="-10.16" y2="7.62" width="0.254" layer="94"/>
<text x="-10.16" y="8.89" size="1.27" layer="95" font="vector">&gt;NAME</text>
<text x="-10.16" y="-10.16" size="1.27" layer="96" font="vector">&gt;VALUE</text>
<wire x1="6.6675" y1="-0.635" x2="7.9375" y2="-0.635" width="0.254" layer="94"/>
<wire x1="7.9375" y1="-0.635" x2="9.2075" y2="-0.635" width="0.254" layer="94"/>
<wire x1="9.2075" y1="-0.635" x2="7.9375" y2="0.635" width="0.254" layer="94"/>
<wire x1="7.9375" y1="0.635" x2="6.6675" y2="-0.635" width="0.254" layer="94"/>
<wire x1="6.6675" y1="0.635" x2="7.9375" y2="0.635" width="0.254" layer="94"/>
<wire x1="7.9375" y1="0.635" x2="9.2075" y2="0.635" width="0.254" layer="94"/>
<wire x1="7.9375" y1="-0.635" x2="7.9375" y2="-1.905" width="0.254" layer="94"/>
<wire x1="7.9375" y1="-1.905" x2="5.3975" y2="-1.905" width="0.254" layer="94"/>
<wire x1="7.9375" y1="0.635" x2="7.9375" y2="1.905" width="0.254" layer="94"/>
<wire x1="7.9375" y1="1.905" x2="5.3975" y2="1.905" width="0.254" layer="94"/>
<wire x1="5.3975" y1="-1.905" x2="5.3975" y2="0" width="0.254" layer="94"/>
<wire x1="5.3975" y1="0" x2="2.8575" y2="0" width="0.254" layer="94"/>
<wire x1="2.8575" y1="0" x2="3.4925" y2="0.3175" width="0.254" layer="94"/>
<wire x1="2.8575" y1="0" x2="3.4925" y2="-0.3175" width="0.254" layer="94"/>
<wire x1="5.3975" y1="1.905" x2="5.3975" y2="3.175" width="0.254" layer="94"/>
<wire x1="5.3975" y1="1.905" x2="2.8575" y2="1.905" width="0.254" layer="94"/>
<wire x1="2.8575" y1="2.54" x2="2.8575" y2="1.27" width="0.254" layer="94"/>
<wire x1="2.8575" y1="0.635" x2="2.8575" y2="-0.635" width="0.254" layer="94"/>
<wire x1="2.8575" y1="-1.27" x2="2.8575" y2="-1.905" width="0.254" layer="94"/>
<wire x1="2.8575" y1="-1.905" x2="2.8575" y2="-2.54" width="0.254" layer="94"/>
<wire x1="5.3975" y1="-1.905" x2="2.8575" y2="-1.905" width="0.254" layer="94"/>
<wire x1="2.2225" y1="2.2225" x2="2.2225" y2="-2.2225" width="0.254" layer="94"/>
<wire x1="5.3975" y1="-1.905" x2="5.3975" y2="-3.175" width="0.254" layer="94"/>
<pin name="GND" x="0" y="-12.7" length="middle" rot="R90"/>
</symbol>
</symbols>
<devicesets>
<deviceset name="ITS428L2" prefix="U" uservalue="yes">
<gates>
<gate name="G$1" symbol="ITS428L2" x="0" y="0"/>
</gates>
<devices>
<device name="" package="PG-TO252-5-11">
<connects>
<connect gate="G$1" pin="GND" pad="1"/>
<connect gate="G$1" pin="IN" pad="2"/>
<connect gate="G$1" pin="ST" pad="4"/>
<connect gate="G$1" pin="VBB" pad="TAB"/>
<connect gate="G$1" pin="VOUT" pad="5"/>
</connects>
<technologies>
<technology name="">
<attribute name="MPN" value="" constant="no"/>
</technology>
</technologies>
</device>
</devices>
</deviceset>
</devicesets>
</library>
<library name="USER_PMIC">
<packages>
<package name="SOT23-5">
<smd name="2" x="-1.3" y="0" dx="0.6" dy="1.1" layer="1" rot="R90"/>
<smd name="3" x="-1.3" y="-0.95" dx="0.6" dy="1.1" layer="1" rot="R90"/>
<smd name="1" x="-1.3" y="0.95" dx="0.6" dy="1.1" layer="1" rot="R90"/>
<smd name="5" x="1.3" y="0.95" dx="0.6" dy="1.1" layer="1" rot="R90"/>
<smd name="4" x="1.3" y="-0.95" dx="0.6" dy="1.1" layer="1" rot="R90"/>
<wire x1="0.8" y1="1.5" x2="-0.9" y2="1.5" width="0.127" layer="21"/>
<wire x1="0.8" y1="-1.5" x2="-0.8" y2="-1.5" width="0.127" layer="21"/>
<wire x1="-0.8" y1="-1.5" x2="-0.9" y2="-1.4" width="0.127" layer="21"/>
<wire x1="0.8" y1="-1.5" x2="0.9" y2="-1.4" width="0.127" layer="21"/>
<wire x1="-0.9" y1="1.5" x2="-1" y2="1.4" width="0.127" layer="21"/>
<wire x1="0.8" y1="1.5" x2="0.9" y2="1.4" width="0.127" layer="21"/>
<wire x1="0.9" y1="0.4" x2="0.9" y2="-0.4" width="0.127" layer="21"/>
<text x="0" y="1.8" size="1" layer="25" font="vector" align="bottom-center">&gt;NAME</text>
</package>
</packages>
<symbols>
<symbol name="TPS3847">
<pin name="VCC" x="0" y="15.24" length="middle" rot="R270"/>
<pin name="!MR" x="-15.24" y="0" length="middle"/>
<pin name="GND" x="0" y="-15.24" length="middle" rot="R90"/>
<pin name="!RST" x="15.24" y="0" length="middle" rot="R180"/>
<wire x1="-10.16" y1="10.16" x2="-10.16" y2="-10.16" width="0.254" layer="94"/>
<wire x1="-10.16" y1="-10.16" x2="10.16" y2="-10.16" width="0.254" layer="94"/>
<wire x1="10.16" y1="-10.16" x2="10.16" y2="10.16" width="0.254" layer="94"/>
<wire x1="10.16" y1="10.16" x2="-10.16" y2="10.16" width="0.254" layer="94"/>
<text x="-10.16" y="11.43" size="1.27" layer="95" font="vector">&gt;NAME</text>
<text x="-10.16" y="-12.7" size="1.27" layer="96" font="vector">&gt;VALUE</text>
</symbol>
</symbols>
<devicesets>
<deviceset name="TPS3847" prefix="U" uservalue="yes">
<gates>
<gate name="G$1" symbol="TPS3847" x="0" y="0"/>
</gates>
<devices>
<device name="" package="SOT23-5">
<connects>
<connect gate="G$1" pin="!MR" pad="4"/>
<connect gate="G$1" pin="!RST" pad="1"/>
<connect gate="G$1" pin="GND" pad="2"/>
<connect gate="G$1" pin="VCC" pad="5"/>
</connects>
<technologies>
<technology name="">
<attribute name="MPN" value="" constant="no"/>
</technology>
</technologies>
</device>
</devices>
</deviceset>
</devicesets>
</library>
<library name="USER_GALOIS_CYBERPHYS">
<packages>
<package name="USB_RELAY_PCB_FOOTPRINT">
<wire x1="-24" y1="-8.5" x2="-4" y2="-8.5" width="0.254" layer="21"/>
<wire x1="-4" y1="-8.5" x2="15.5" y2="-8.5" width="0.254" layer="21"/>
<wire x1="15.5" y1="-8.5" x2="16.5" y2="-8.5" width="0.254" layer="21"/>
<wire x1="16.5" y1="-8.5" x2="24" y2="-8.5" width="0.254" layer="21"/>
<wire x1="24" y1="-8.5" x2="24" y2="-5.08" width="0.254" layer="21"/>
<wire x1="24" y1="-5.08" x2="24" y2="0" width="0.254" layer="21"/>
<wire x1="24" y1="0" x2="24" y2="5.008" width="0.254" layer="21"/>
<wire x1="24" y1="5.008" x2="24" y2="8.5" width="0.254" layer="21"/>
<wire x1="24" y1="8.5" x2="16.5" y2="8.5" width="0.254" layer="21"/>
<wire x1="16.5" y1="8.5" x2="15.5" y2="8.5" width="0.254" layer="21"/>
<wire x1="15.5" y1="8.5" x2="-4" y2="8.5" width="0.254" layer="21"/>
<wire x1="-4" y1="8.5" x2="-24" y2="8.5" width="0.254" layer="21"/>
<wire x1="-24" y1="8.5" x2="-24" y2="6" width="0.254" layer="21"/>
<wire x1="-24" y1="6" x2="-24" y2="-6" width="0.254" layer="21"/>
<wire x1="-24" y1="-6" x2="-24" y2="-8.5" width="0.254" layer="21"/>
<wire x1="-24" y1="-6" x2="-40" y2="-6" width="0.254" layer="21"/>
<wire x1="-40" y1="-6" x2="-40" y2="6" width="0.254" layer="21"/>
<wire x1="-40" y1="6" x2="-24" y2="6" width="0.254" layer="21"/>
<text x="-32" y="0" size="2" layer="21" font="vector" align="center">USB A</text>
<text x="5.5" y="0" size="2" layer="21" font="vector" align="center">RELAY</text>
<wire x1="16.5" y1="-8.5" x2="16.5" y2="8.5" width="0.254" layer="21" style="shortdash"/>
<text x="15.5" y="0" size="1" layer="21" font="vector" rot="R90" align="bottom-center">200 MIL PITCH
HEADER STOP</text>
<wire x1="24" y1="0" x2="22" y2="0" width="0.254" layer="21"/>
<wire x1="24" y1="5.008" x2="22" y2="5.008" width="0.254" layer="21"/>
<wire x1="24" y1="-5.08" x2="22" y2="-5.08" width="0.254" layer="21"/>
<text x="21.25" y="0" size="1" layer="21" font="vector" rot="R180" align="center-left">COM</text>
<text x="21.25" y="-5" size="1" layer="21" font="vector" rot="R180" align="center-left">NO</text>
<text x="21.25" y="5" size="1" layer="21" font="vector" rot="R180" align="center-left">NC</text>
<wire x1="-4" y1="-8.5" x2="-4" y2="8.5" width="0.254" layer="21"/>
<wire x1="15.5" y1="-8.5" x2="15.5" y2="-5.5" width="0.254" layer="21"/>
<wire x1="15.5" y1="8.5" x2="15.5" y2="5.5" width="0.254" layer="21"/>
</package>
<package name="FADECANDY_PCB_FOOTPRINT">
<circle x="17.78" y="8.89" radius="0.635" width="0.3302" layer="21"/>
<circle x="15.24" y="8.89" radius="0.635" width="0.3302" layer="21"/>
<circle x="15.24" y="6.35" radius="0.635" width="0.3302" layer="21"/>
<circle x="17.78" y="6.35" radius="0.635" width="0.3302" layer="21"/>
<circle x="17.78" y="3.81" radius="0.635" width="0.3302" layer="21"/>
<circle x="15.24" y="3.81" radius="0.635" width="0.3302" layer="21"/>
<circle x="15.24" y="1.27" radius="0.635" width="0.3302" layer="21"/>
<circle x="17.78" y="1.27" radius="0.635" width="0.3302" layer="21"/>
<circle x="17.78" y="-1.27" radius="0.635" width="0.3302" layer="21"/>
<circle x="15.24" y="-1.27" radius="0.635" width="0.3302" layer="21"/>
<circle x="15.24" y="-3.81" radius="0.635" width="0.3302" layer="21"/>
<circle x="17.78" y="-3.81" radius="0.635" width="0.3302" layer="21"/>
<circle x="17.78" y="-6.35" radius="0.635" width="0.3302" layer="21"/>
<circle x="15.24" y="-6.35" radius="0.635" width="0.3302" layer="21"/>
<circle x="15.24" y="-8.89" radius="0.635" width="0.3302" layer="21"/>
<circle x="17.78" y="-8.89" radius="0.635" width="0.3302" layer="21"/>
<wire x1="19.05" y1="-8.89" x2="17.78" y2="-10.16" width="0.254" layer="21" curve="-90"/>
<wire x1="17.78" y1="-10.16" x2="-17.78" y2="-10.16" width="0.254" layer="21"/>
<wire x1="-17.78" y1="-10.16" x2="-19.05" y2="-8.89" width="0.254" layer="21" curve="-90"/>
<wire x1="-19.05" y1="-8.89" x2="-19.05" y2="-3.5" width="0.254" layer="21"/>
<wire x1="-19.05" y1="3.5" x2="-19.05" y2="8.89" width="0.254" layer="21"/>
<wire x1="-19.05" y1="8.89" x2="-17.78" y2="10.16" width="0.254" layer="21" curve="-90"/>
<wire x1="-17.78" y1="10.16" x2="17.78" y2="10.16" width="0.254" layer="21"/>
<wire x1="17.78" y1="10.16" x2="19.05" y2="8.89" width="0.254" layer="21" curve="-90"/>
<wire x1="19.05" y1="8.89" x2="19.05" y2="-8.89" width="0.254" layer="21"/>
<wire x1="-19.05" y1="3.5" x2="-10.55" y2="3.5" width="0.254" layer="21"/>
<wire x1="-10.55" y1="3.5" x2="-10.55" y2="-3.5" width="0.254" layer="21"/>
<wire x1="-10.55" y1="-3.5" x2="-19.05" y2="-3.5" width="0.254" layer="21"/>
<wire x1="-19.05" y1="-3.5" x2="-19.55" y2="-3.5" width="0.254" layer="21"/>
<wire x1="-19.55" y1="-3.5" x2="-19.55" y2="3.5" width="0.254" layer="21"/>
<wire x1="-19.55" y1="3.5" x2="-19.05" y2="3.5" width="0.254" layer="21"/>
<text x="0" y="0" size="1.778" layer="21" align="center">FADECANDY
LED DRIVER
PCBA</text>
</package>
</packages>
<symbols>
<symbol name="USB_RELAY_PCB_FOOTPRINT">
<circle x="19.021" y="0.001" radius="1.905" width="0.254" layer="94"/>
<circle x="19.021" y="5.081" radius="1.905" width="0.254" layer="94"/>
<circle x="19.021" y="-5.079" radius="1.905" width="0.254" layer="94"/>
<wire x1="22.021" y1="8.001" x2="22.021" y2="-7.999" width="0.254" layer="94"/>
<wire x1="22.021" y1="-7.999" x2="16.021" y2="-7.999" width="0.254" layer="94"/>
<wire x1="16.021" y1="-7.999" x2="16.021" y2="8.001" width="0.254" layer="94"/>
<wire x1="16.021" y1="8.001" x2="22.021" y2="8.001" width="0.254" layer="94"/>
<wire x1="16.021" y1="-7.999" x2="-1.979" y2="-7.999" width="0.254" layer="94"/>
<wire x1="-1.979" y1="-7.999" x2="-1.979" y2="8.001" width="0.254" layer="94"/>
<wire x1="-1.979" y1="8.001" x2="16.021" y2="8.001" width="0.254" layer="94"/>
<wire x1="-1.979" y1="-7.999" x2="-6.979" y2="-7.999" width="0.254" layer="94"/>
<wire x1="-6.979" y1="-7.999" x2="-13.979" y2="-7.999" width="0.254" layer="94"/>
<wire x1="-13.979" y1="-7.999" x2="-21.979" y2="-7.999" width="0.254" layer="94"/>
<wire x1="-21.979" y1="-7.999" x2="-21.979" y2="-5.999" width="0.254" layer="94"/>
<wire x1="-21.979" y1="8.001" x2="-1.979" y2="8.001" width="0.254" layer="94"/>
<wire x1="-21.979" y1="-5.999" x2="-37.979" y2="-5.999" width="0.254" layer="94"/>
<wire x1="-37.979" y1="-5.999" x2="-37.979" y2="6.001" width="0.254" layer="94"/>
<wire x1="-37.979" y1="6.001" x2="-21.979" y2="6.001" width="0.254" layer="94"/>
<wire x1="-21.979" y1="6.001" x2="-18.979" y2="6.001" width="0.254" layer="94"/>
<wire x1="-18.979" y1="6.001" x2="-18.979" y2="3.001" width="0.254" layer="94"/>
<wire x1="-18.979" y1="3.001" x2="-18.979" y2="1.001" width="0.254" layer="94"/>
<wire x1="-18.979" y1="1.001" x2="-18.979" y2="-0.999" width="0.254" layer="94"/>
<wire x1="-18.979" y1="-0.999" x2="-18.979" y2="-2.999" width="0.254" layer="94"/>
<wire x1="-18.979" y1="-2.999" x2="-18.979" y2="-5.999" width="0.254" layer="94"/>
<wire x1="-18.979" y1="-5.999" x2="-21.979" y2="-5.999" width="0.254" layer="94"/>
<wire x1="-21.979" y1="8.001" x2="-21.979" y2="6.001" width="0.254" layer="94"/>
<wire x1="-13.979" y1="-7.999" x2="-13.979" y2="-3.999" width="0.254" layer="94" curve="-180"/>
<wire x1="-6.979" y1="-3.999" x2="-6.979" y2="-7.999" width="0.254" layer="94" curve="-180"/>
<wire x1="-13.979" y1="-3.999" x2="-6.979" y2="-3.999" width="0.254" layer="94"/>
<wire x1="-12.979" y1="-2.999" x2="-7.979" y2="-2.999" width="0.254" layer="94"/>
<wire x1="-7.979" y1="4.001" x2="-12.979" y2="4.001" width="0.254" layer="94"/>
<wire x1="-12.979" y1="4.001" x2="-12.979" y2="3.751" width="0.254" layer="94"/>
<wire x1="-12.979" y1="3.751" x2="-12.979" y2="3.251" width="0.254" layer="94"/>
<wire x1="-12.979" y1="3.251" x2="-12.979" y2="2.751" width="0.254" layer="94"/>
<wire x1="-12.979" y1="2.751" x2="-12.979" y2="2.251" width="0.254" layer="94"/>
<wire x1="-12.979" y1="2.251" x2="-12.979" y2="1.751" width="0.254" layer="94"/>
<wire x1="-12.979" y1="1.751" x2="-12.979" y2="1.251" width="0.254" layer="94"/>
<wire x1="-12.979" y1="1.251" x2="-12.979" y2="0.751" width="0.254" layer="94"/>
<wire x1="-12.979" y1="0.751" x2="-12.979" y2="0.251" width="0.254" layer="94"/>
<wire x1="-12.979" y1="0.251" x2="-12.979" y2="-0.249" width="0.254" layer="94"/>
<wire x1="-12.979" y1="-0.249" x2="-12.979" y2="-0.749" width="0.254" layer="94"/>
<wire x1="-12.979" y1="-0.749" x2="-12.979" y2="-1.249" width="0.254" layer="94"/>
<wire x1="-12.979" y1="-1.249" x2="-12.979" y2="-1.749" width="0.254" layer="94"/>
<wire x1="-12.979" y1="-1.749" x2="-12.979" y2="-2.249" width="0.254" layer="94"/>
<wire x1="-12.979" y1="-2.249" x2="-12.979" y2="-2.749" width="0.254" layer="94"/>
<wire x1="-12.979" y1="-2.749" x2="-12.979" y2="-2.999" width="0.254" layer="94"/>
<wire x1="-18.979" y1="1.001" x2="-16.979" y2="1.001" width="0.254" layer="94"/>
<wire x1="-18.979" y1="-0.999" x2="-16.979" y2="-0.999" width="0.254" layer="94"/>
<wire x1="-18.979" y1="-2.999" x2="-16.979" y2="-2.999" width="0.254" layer="94"/>
<wire x1="-18.979" y1="3.001" x2="-16.979" y2="3.001" width="0.254" layer="94"/>
<wire x1="-12.979" y1="-2.749" x2="-14.479" y2="-2.749" width="0.254" layer="94"/>
<wire x1="-12.979" y1="-2.249" x2="-14.479" y2="-2.249" width="0.254" layer="94"/>
<wire x1="-12.979" y1="-1.749" x2="-14.479" y2="-1.749" width="0.254" layer="94"/>
<wire x1="-12.979" y1="-1.249" x2="-14.479" y2="-1.249" width="0.254" layer="94"/>
<wire x1="-12.979" y1="-0.749" x2="-14.479" y2="-0.749" width="0.254" layer="94"/>
<wire x1="-12.979" y1="-0.249" x2="-14.479" y2="-0.249" width="0.254" layer="94"/>
<wire x1="-12.979" y1="0.251" x2="-14.479" y2="0.251" width="0.254" layer="94"/>
<wire x1="-12.979" y1="0.751" x2="-14.479" y2="0.751" width="0.254" layer="94"/>
<wire x1="-12.979" y1="1.251" x2="-14.479" y2="1.251" width="0.254" layer="94"/>
<wire x1="-12.979" y1="1.751" x2="-14.479" y2="1.751" width="0.254" layer="94"/>
<wire x1="-12.979" y1="2.251" x2="-14.479" y2="2.251" width="0.254" layer="94"/>
<wire x1="-12.979" y1="2.751" x2="-14.479" y2="2.751" width="0.254" layer="94"/>
<wire x1="-12.979" y1="3.251" x2="-14.479" y2="3.251" width="0.254" layer="94"/>
<wire x1="-12.979" y1="3.751" x2="-14.479" y2="3.751" width="0.254" layer="94"/>
<wire x1="-7.979" y1="-2.999" x2="-7.979" y2="-2.749" width="0.254" layer="94"/>
<wire x1="-7.979" y1="-2.749" x2="-7.979" y2="-2.249" width="0.254" layer="94"/>
<wire x1="-7.979" y1="-2.249" x2="-7.979" y2="-1.749" width="0.254" layer="94"/>
<wire x1="-7.979" y1="-1.749" x2="-7.979" y2="-1.249" width="0.254" layer="94"/>
<wire x1="-7.979" y1="-1.249" x2="-7.979" y2="-0.749" width="0.254" layer="94"/>
<wire x1="-7.979" y1="-0.749" x2="-7.979" y2="-0.249" width="0.254" layer="94"/>
<wire x1="-7.979" y1="-0.249" x2="-7.979" y2="0.251" width="0.254" layer="94"/>
<wire x1="-7.979" y1="0.251" x2="-7.979" y2="0.751" width="0.254" layer="94"/>
<wire x1="-7.979" y1="0.751" x2="-7.979" y2="1.251" width="0.254" layer="94"/>
<wire x1="-7.979" y1="1.251" x2="-7.979" y2="1.751" width="0.254" layer="94"/>
<wire x1="-7.979" y1="1.751" x2="-7.979" y2="2.251" width="0.254" layer="94"/>
<wire x1="-7.979" y1="2.251" x2="-7.979" y2="2.751" width="0.254" layer="94"/>
<wire x1="-7.979" y1="2.751" x2="-7.979" y2="3.251" width="0.254" layer="94"/>
<wire x1="-7.979" y1="3.251" x2="-7.979" y2="3.751" width="0.254" layer="94"/>
<wire x1="-7.979" y1="3.751" x2="-7.979" y2="4.001" width="0.254" layer="94"/>
<wire x1="-7.979" y1="3.751" x2="-6.479" y2="3.751" width="0.254" layer="94"/>
<wire x1="-7.979" y1="3.251" x2="-6.479" y2="3.251" width="0.254" layer="94"/>
<wire x1="-7.979" y1="2.751" x2="-6.479" y2="2.751" width="0.254" layer="94"/>
<wire x1="-7.979" y1="2.251" x2="-6.479" y2="2.251" width="0.254" layer="94"/>
<wire x1="-7.979" y1="1.751" x2="-6.479" y2="1.751" width="0.254" layer="94"/>
<wire x1="-7.979" y1="1.251" x2="-6.479" y2="1.251" width="0.254" layer="94"/>
<wire x1="-7.979" y1="0.751" x2="-6.479" y2="0.751" width="0.254" layer="94"/>
<wire x1="-7.979" y1="0.251" x2="-6.479" y2="0.251" width="0.254" layer="94"/>
<wire x1="-7.979" y1="-0.249" x2="-6.479" y2="-0.249" width="0.254" layer="94"/>
<wire x1="-7.979" y1="-0.749" x2="-6.479" y2="-0.749" width="0.254" layer="94"/>
<wire x1="-7.979" y1="-1.249" x2="-6.479" y2="-1.249" width="0.254" layer="94"/>
<wire x1="-7.979" y1="-1.749" x2="-6.479" y2="-1.749" width="0.254" layer="94"/>
<wire x1="-7.979" y1="-2.249" x2="-6.479" y2="-2.249" width="0.254" layer="94"/>
<wire x1="-7.979" y1="-2.749" x2="-6.479" y2="-2.749" width="0.254" layer="94"/>
<rectangle x1="16.771" y1="2.251" x2="21.271" y2="2.751" layer="94"/>
<rectangle x1="16.771" y1="-2.749" x2="21.271" y2="-2.249" layer="94"/>
<text x="7.021" y="0.001" size="2" layer="94" font="vector" align="center">RELAY</text>
<wire x1="17.771" y1="5.501" x2="20.271" y2="4.501" width="0.254" layer="94"/>
<wire x1="18.521" y1="-1.249" x2="19.521" y2="1.251" width="0.254" layer="94"/>
<wire x1="19.521" y1="-6.249" x2="18.521" y2="-3.749" width="0.254" layer="94"/>
<text x="15.367" y="0" size="1.27" layer="94" font="vector" rot="R180" align="center-left">COM</text>
<text x="15.367" y="-5.08" size="1.27" layer="94" font="vector" rot="R180" align="center-left">NO</text>
<text x="15.367" y="4.953" size="1.27" layer="94" font="vector" rot="R180" align="center-left">NC</text>
</symbol>
<symbol name="FADECANDY_PCB_FOOTPRINT">
<circle x="17.78" y="1.27" radius="0.635" width="0.254" layer="94"/>
<circle x="17.78" y="-1.27" radius="0.635" width="0.254" layer="94"/>
<circle x="17.78" y="-3.81" radius="0.635" width="0.254" layer="94"/>
<circle x="17.78" y="-6.35" radius="0.635" width="0.254" layer="94"/>
<circle x="17.78" y="-8.89" radius="0.635" width="0.254" layer="94"/>
<circle x="17.78" y="3.81" radius="0.635" width="0.254" layer="94"/>
<circle x="17.78" y="6.35" radius="0.635" width="0.254" layer="94"/>
<circle x="17.78" y="8.89" radius="0.635" width="0.254" layer="94"/>
<circle x="15.24" y="-8.89" radius="0.635" width="0.254" layer="94"/>
<circle x="15.24" y="-6.35" radius="0.635" width="0.254" layer="94"/>
<circle x="15.24" y="-3.81" radius="0.635" width="0.254" layer="94"/>
<circle x="15.24" y="-1.27" radius="0.635" width="0.254" layer="94"/>
<circle x="15.24" y="1.27" radius="0.635" width="0.254" layer="94"/>
<circle x="15.24" y="3.81" radius="0.635" width="0.254" layer="94"/>
<circle x="15.24" y="6.35" radius="0.635" width="0.254" layer="94"/>
<circle x="15.24" y="8.89" radius="0.635" width="0.254" layer="94"/>
<wire x1="19.05" y1="-8.89" x2="17.78" y2="-10.16" width="0.254" layer="94" curve="-90"/>
<wire x1="17.78" y1="-10.16" x2="-17.78" y2="-10.16" width="0.254" layer="94"/>
<wire x1="-17.78" y1="-10.16" x2="-19.05" y2="-8.89" width="0.254" layer="94" curve="-90"/>
<wire x1="-19.05" y1="8.89" x2="-17.78" y2="10.16" width="0.254" layer="94" curve="-90"/>
<wire x1="-17.78" y1="10.16" x2="17.78" y2="10.16" width="0.254" layer="94"/>
<wire x1="17.78" y1="10.16" x2="19.05" y2="8.89" width="0.254" layer="94" curve="-90"/>
<wire x1="19.05" y1="8.89" x2="19.05" y2="-8.89" width="0.254" layer="94"/>
<wire x1="-19.05" y1="8.89" x2="-19.05" y2="3.5" width="0.254" layer="94"/>
<wire x1="-19.05" y1="3.5" x2="-10.55" y2="3.5" width="0.254" layer="94"/>
<wire x1="-10.55" y1="3.5" x2="-10.55" y2="-3.5" width="0.254" layer="94"/>
<wire x1="-10.55" y1="-3.5" x2="-19.05" y2="-3.5" width="0.254" layer="94"/>
<wire x1="-19.05" y1="-3.5" x2="-19.55" y2="-3.5" width="0.254" layer="94"/>
<wire x1="-19.55" y1="-3.5" x2="-19.55" y2="3.5" width="0.254" layer="94"/>
<wire x1="-19.55" y1="3.5" x2="-19.05" y2="3.5" width="0.254" layer="94"/>
<wire x1="-19.05" y1="-9" x2="-19.05" y2="-3.5" width="0.254" layer="94"/>
<text x="0" y="0" size="2" layer="94" align="center">FADECANDY
LED DRIVER
PCBA</text>
</symbol>
</symbols>
<devicesets>
<deviceset name="USB_RELAY_PCB_FOOTPRINT">
<gates>
<gate name="G$1" symbol="USB_RELAY_PCB_FOOTPRINT" x="0" y="0"/>
</gates>
<devices>
<device name="" package="USB_RELAY_PCB_FOOTPRINT">
<technologies>
<technology name=""/>
</technologies>
</device>
</devices>
</deviceset>
<deviceset name="FADECANDY_PCB_FOOTPRINT">
<gates>
<gate name="G$1" symbol="FADECANDY_PCB_FOOTPRINT" x="0" y="0"/>
</gates>
<devices>
<device name="" package="FADECANDY_PCB_FOOTPRINT">
<technologies>
<technology name=""/>
</technologies>
</device>
</devices>
</deviceset>
</devicesets>
</library>
<library name="USER_CAPACITORS_ELECTROLYTIC">
<packages>
<package name="PANASONIC_TQC_B">
<wire x1="-1.7" y1="1.4" x2="-1.7" y2="-1.4" width="0.127" layer="21"/>
<wire x1="-1.7" y1="-1.4" x2="1.7" y2="-1.4" width="0.127" layer="21"/>
<wire x1="1.7" y1="-1.4" x2="1.7" y2="1.4" width="0.127" layer="21"/>
<wire x1="1.7" y1="1.4" x2="-1.7" y2="1.4" width="0.127" layer="21"/>
<smd name="C+" x="-1.5" y="0" dx="2.5" dy="1.4" layer="1" rot="R90"/>
<smd name="C-" x="1.5" y="0" dx="2.5" dy="1.4" layer="1" rot="R90"/>
<rectangle x1="-2.8" y1="-1.4" x2="-2.4" y2="1.4" layer="21"/>
<text x="0" y="-2.794" size="1.016" layer="21" font="vector" align="bottom-center">&gt;NAME</text>
<rectangle x1="-2.921" y1="-1.651" x2="2.413" y2="1.651" layer="39"/>
</package>
<package name="NICHICON_PCR_8DIAX10H">
<circle x="0" y="0" radius="4" width="0.127" layer="21"/>
<wire x1="4.2" y1="-4.2" x2="4.2" y2="2.7" width="0.127" layer="21"/>
<wire x1="4.2" y1="2.7" x2="2.7" y2="4.2" width="0.127" layer="21"/>
<wire x1="2.7" y1="4.2" x2="-2.7" y2="4.2" width="0.127" layer="21"/>
<wire x1="-2.7" y1="4.2" x2="-4.2" y2="2.7" width="0.127" layer="21"/>
<wire x1="-4.2" y1="2.7" x2="-4.2" y2="-4.2" width="0.127" layer="21"/>
<wire x1="-4.2" y1="-4.2" x2="4.2" y2="-4.2" width="0.127" layer="21"/>
<smd name="C-" x="0" y="-3.6" dx="1.5" dy="4" layer="1"/>
<smd name="C+" x="0" y="3.6" dx="1.5" dy="4" layer="1"/>
<text x="-5" y="-4" size="1" layer="25" font="vector" rot="R90">&gt;NAME</text>
</package>
<package name="NICHICON_UHE_7.5MM">
<pad name="C+" x="-3.75" y="0" drill="1" diameter="1.8" shape="square"/>
<pad name="C-" x="3.75" y="0" drill="1" diameter="1.8"/>
<circle x="0" y="0" radius="9" width="0.127" layer="21"/>
<text x="-11" y="0" size="2" layer="21" font="vector" rot="R90" align="center">+</text>
<text x="0" y="10" size="1" layer="25" font="vector" align="bottom-center">&gt;NAME</text>
</package>
<package name="TYPE_SLPX_10MM">
<pad name="C+" x="-5" y="0" drill="2" diameter="4" shape="square"/>
<pad name="C-" x="5" y="0" drill="2" diameter="4"/>
<circle x="0" y="0" radius="15" width="0.127" layer="21"/>
<text x="-16" y="-4" size="1" layer="21" font="vector" rot="R90" align="bottom-center">&gt;NAME</text>
<text x="-16" y="0" size="2" layer="21" font="vector" ratio="15" rot="R90" align="bottom-center">+</text>
</package>
<package name="PANASONIC_FC_7.5MM">
<pad name="C+" x="-3.75" y="0" drill="1.2" shape="square"/>
<pad name="C-" x="3.75" y="0" drill="1.2"/>
<circle x="0" y="0" radius="8" width="0.127" layer="21"/>
<text x="-8.5" y="0" size="2" layer="21" font="vector" ratio="15" rot="R90" align="bottom-center">+</text>
<text x="-9.25" y="1.25" size="1" layer="21" font="vector" align="bottom-center">&gt;NAME</text>
</package>
<package name="PANASONIC_FT_SMT_D8">
<smd name="C+" x="0" y="3.5" dx="2" dy="3.8" layer="1"/>
<smd name="C-" x="0" y="-3.5" dx="2" dy="3.8" layer="1"/>
<circle x="0" y="0" radius="3.2" width="0.127" layer="51"/>
<wire x1="3.4" y1="1.6" x2="3.4" y2="-3.4" width="0.127" layer="21"/>
<wire x1="-3.4" y1="-3.4" x2="-3.4" y2="1.6" width="0.127" layer="21"/>
<wire x1="-1.6" y1="3.4" x2="-3.4" y2="1.6" width="0.127" layer="21"/>
<wire x1="1.6" y1="3.4" x2="3.4" y2="1.6" width="0.127" layer="21"/>
<wire x1="-3.4" y1="-3.4" x2="-1.4" y2="-3.4" width="0.127" layer="21"/>
<wire x1="3.4" y1="-3.4" x2="1.4" y2="-3.4" width="0.127" layer="21"/>
<wire x1="-1.6" y1="3.4" x2="-1.4" y2="3.4" width="0.127" layer="21"/>
<wire x1="1.6" y1="3.4" x2="1.4" y2="3.4" width="0.127" layer="21"/>
<text x="-1.6" y="4.2" size="1" layer="21" font="vector" rot="R180" align="center">+</text>
<text x="-3.8" y="0" size="1" layer="25" font="vector" rot="R90" align="bottom-center">&gt;NAME</text>
<pad name="P$1" x="-0.5" y="5" drill="0.3"/>
<pad name="P$2" x="0.5" y="5" drill="0.3"/>
<pad name="P$3" x="0.5" y="4" drill="0.3"/>
<pad name="P$4" x="-0.5" y="4" drill="0.3"/>
<pad name="P$5" x="-0.5" y="3" drill="0.3"/>
<pad name="P$6" x="0.5" y="3" drill="0.3"/>
<pad name="P$7" x="0.5" y="2" drill="0.3"/>
<pad name="P$8" x="-0.5" y="2" drill="0.3"/>
</package>
<package name="NICHICON_ULD_3.5MM">
<pad name="C+" x="-1.75" y="0" drill="0.6"/>
<pad name="C-" x="1.75" y="0" drill="0.6"/>
<circle x="0" y="0" radius="4" width="0.127" layer="21"/>
<text x="-4.75" y="0" size="1.27" layer="21" font="vector" rot="R180" align="center">+</text>
<text x="0" y="-4.5" size="1" layer="21" font="vector" rot="R180" align="bottom-center">&gt;NAME</text>
</package>
<package name="PANASONIC_FC_5MM_SIDE">
<wire x1="0" y1="6.5" x2="0" y2="-6.5" width="0.127" layer="21"/>
<wire x1="0" y1="-6.5" x2="40" y2="-6.5" width="0.127" layer="21"/>
<wire x1="40" y1="-6.5" x2="40" y2="6.5" width="0.127" layer="21"/>
<wire x1="40" y1="6.5" x2="0" y2="6.5" width="0.127" layer="21"/>
<pad name="C+" x="43" y="2.5" drill="1" shape="square"/>
<pad name="C-" x="43" y="-2.5" drill="1"/>
<rectangle x1="40" y1="2" x2="42" y2="3" layer="21"/>
<rectangle x1="40" y1="-3" x2="42" y2="-2" layer="21"/>
<text x="43" y="3.5" size="1.27" layer="21" font="vector" align="bottom-center">+</text>
</package>
<package name="PANASONIC_HD_12.5MM">
<pad name="C+" x="-2.5" y="0" drill="1" diameter="2" shape="square"/>
<pad name="C-" x="2.5" y="0" drill="1" diameter="2"/>
<circle x="0" y="0" radius="6.25" width="0.254" layer="21"/>
<text x="-7.25" y="0.25" size="2" layer="21" font="vector" rot="R180" align="center">+</text>
<text x="0" y="6.75" size="1" layer="25" font="vector" align="bottom-center">&gt;NAME</text>
</package>
</packages>
<symbols>
<symbol name="C_POLARIZED">
<wire x1="-2.54" y1="1.27" x2="2.54" y2="1.27" width="0.254" layer="94"/>
<wire x1="-2.54" y1="-1.27" x2="2.54" y2="-1.27" width="0.254" layer="94" curve="-106.260205"/>
<pin name="C+" x="0" y="3.81" visible="off" length="short" rot="R270"/>
<pin name="C-" x="0" y="-2.54" visible="off" length="short" rot="R90"/>
<text x="3.81" y="1.27" size="1.27" layer="95" font="vector">&gt;NAME</text>
<text x="3.81" y="-1.27" size="1.27" layer="96" font="vector">&gt;VALUE</text>
</symbol>
</symbols>
<devicesets>
<deviceset name="C_POLARIZED" prefix="C" uservalue="yes">
<gates>
<gate name="G$1" symbol="C_POLARIZED" x="0" y="0"/>
</gates>
<devices>
<device name="PANASONIC_TQC_B" package="PANASONIC_TQC_B">
<connects>
<connect gate="G$1" pin="C+" pad="C+"/>
<connect gate="G$1" pin="C-" pad="C-"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="NICHICON_PCR_8X10_SMT" package="NICHICON_PCR_8DIAX10H">
<connects>
<connect gate="G$1" pin="C+" pad="C+"/>
<connect gate="G$1" pin="C-" pad="C-"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="DIA_18MM" package="NICHICON_UHE_7.5MM">
<connects>
<connect gate="G$1" pin="C+" pad="C+"/>
<connect gate="G$1" pin="C-" pad="C-"/>
</connects>
<technologies>
<technology name="">
<attribute name="MPN" value="" constant="no"/>
</technology>
</technologies>
</device>
<device name="SLPX_10MM_SNAP_IN" package="TYPE_SLPX_10MM">
<connects>
<connect gate="G$1" pin="C+" pad="C+"/>
<connect gate="G$1" pin="C-" pad="C-"/>
</connects>
<technologies>
<technology name="">
<attribute name="MPN" value="" constant="no"/>
</technology>
</technologies>
</device>
<device name="PANASONIC_FC_7.5MM" package="PANASONIC_FC_7.5MM">
<connects>
<connect gate="G$1" pin="C+" pad="C+"/>
<connect gate="G$1" pin="C-" pad="C-"/>
</connects>
<technologies>
<technology name="">
<attribute name="MPN" value="" constant="no"/>
</technology>
</technologies>
</device>
<device name="WITH_C+_VIAS" package="PANASONIC_FT_SMT_D8">
<connects>
<connect gate="G$1" pin="C+" pad="C+ P$1 P$2 P$3 P$4 P$5 P$6 P$7 P$8"/>
<connect gate="G$1" pin="C-" pad="C-"/>
</connects>
<technologies>
<technology name="">
<attribute name="MPN" value="" constant="no"/>
</technology>
</technologies>
</device>
<device name="DIA_8MM" package="NICHICON_ULD_3.5MM">
<connects>
<connect gate="G$1" pin="C+" pad="C+"/>
<connect gate="G$1" pin="C-" pad="C-"/>
</connects>
<technologies>
<technology name="">
<attribute name="MPN" value="" constant="no"/>
</technology>
</technologies>
</device>
<device name="DIA_12.5MM_FLAT_40MM" package="PANASONIC_FC_5MM_SIDE">
<connects>
<connect gate="G$1" pin="C+" pad="C+"/>
<connect gate="G$1" pin="C-" pad="C-"/>
</connects>
<technologies>
<technology name="">
<attribute name="MPN" value="" constant="no"/>
</technology>
</technologies>
</device>
<device name="_DIA_12.5MM_LEADS_5MM" package="PANASONIC_HD_12.5MM">
<connects>
<connect gate="G$1" pin="C+" pad="C+"/>
<connect gate="G$1" pin="C-" pad="C-"/>
</connects>
<technologies>
<technology name="">
<attribute name="MPN" value="" constant="no"/>
</technology>
</technologies>
</device>
</devices>
</deviceset>
</devicesets>
</library>
<library name="USER_CON_PINS">
<packages>
<package name="2X8_100MIL">
<pad name="1" x="-1.27" y="8.89" drill="1.1" shape="square"/>
<pad name="2" x="1.27" y="8.89" drill="1.1"/>
<pad name="3" x="-1.27" y="6.35" drill="1.1"/>
<pad name="4" x="1.27" y="6.35" drill="1.1"/>
<pad name="5" x="-1.27" y="3.81" drill="1.1"/>
<pad name="6" x="1.27" y="3.81" drill="1.1"/>
<pad name="7" x="-1.27" y="1.27" drill="1.1"/>
<pad name="8" x="1.27" y="1.27" drill="1.1"/>
<pad name="9" x="-1.27" y="-1.27" drill="1.1"/>
<pad name="10" x="1.27" y="-1.27" drill="1.1"/>
<pad name="11" x="-1.27" y="-3.81" drill="1.1"/>
<pad name="12" x="1.27" y="-3.81" drill="1.1"/>
<pad name="13" x="-1.27" y="-6.35" drill="1.1"/>
<pad name="14" x="1.27" y="-6.35" drill="1.1"/>
<pad name="15" x="-1.27" y="-8.89" drill="1.1"/>
<pad name="16" x="1.27" y="-8.89" drill="1.1"/>
<wire x1="-2.54" y1="10.16" x2="2.54" y2="10.16" width="0.127" layer="21"/>
<wire x1="2.54" y1="10.16" x2="2.54" y2="-10.16" width="0.127" layer="21"/>
<wire x1="2.54" y1="-10.16" x2="-2.54" y2="-10.16" width="0.127" layer="21"/>
<wire x1="-2.54" y1="-10.16" x2="-2.54" y2="10.16" width="0.127" layer="21"/>
<text x="-2.54" y="11.43" size="1.27" layer="25" font="vector">&gt;NAME</text>
</package>
<package name="2X8_100MIL_R/A">
<pad name="1" x="-1.27" y="8.89" drill="1.1" shape="square"/>
<pad name="2" x="1.27" y="8.89" drill="1.1"/>
<pad name="3" x="-1.27" y="6.35" drill="1.1"/>
<pad name="4" x="1.27" y="6.35" drill="1.1"/>
<pad name="5" x="-1.27" y="3.81" drill="1.1"/>
<pad name="6" x="1.27" y="3.81" drill="1.1"/>
<pad name="7" x="-1.27" y="1.27" drill="1.1"/>
<pad name="8" x="1.27" y="1.27" drill="1.1"/>
<pad name="9" x="-1.27" y="-1.27" drill="1.1"/>
<pad name="10" x="1.27" y="-1.27" drill="1.1"/>
<pad name="11" x="-1.27" y="-3.81" drill="1.1"/>
<pad name="12" x="1.27" y="-3.81" drill="1.1"/>
<pad name="13" x="-1.27" y="-6.35" drill="1.1"/>
<pad name="14" x="1.27" y="-6.35" drill="1.1"/>
<pad name="15" x="-1.27" y="-8.89" drill="1.1"/>
<pad name="16" x="1.27" y="-8.89" drill="1.1"/>
<text x="2.75" y="10.75" size="1" layer="25" font="vector">&gt;NAME</text>
<wire x1="11.303" y1="-10.414" x2="11.303" y2="8.255" width="0.127" layer="21"/>
<wire x1="11.303" y1="9.652" x2="11.303" y2="10.414" width="0.127" layer="21"/>
<wire x1="11.303" y1="10.414" x2="2.794" y2="10.414" width="0.127" layer="21"/>
<wire x1="2.794" y1="10.414" x2="2.794" y2="-10.414" width="0.127" layer="21"/>
<wire x1="2.794" y1="-10.414" x2="11.303" y2="-10.414" width="0.127" layer="21"/>
<rectangle x1="2.286" y1="8.763" x2="2.794" y2="9.017" layer="21"/>
<rectangle x1="2.286" y1="6.223" x2="2.794" y2="6.477" layer="21"/>
<rectangle x1="2.286" y1="3.683" x2="2.794" y2="3.937" layer="21"/>
<rectangle x1="-0.254" y1="8.763" x2="0.254" y2="9.017" layer="21"/>
<rectangle x1="-0.254" y1="6.223" x2="0.254" y2="6.477" layer="21"/>
<rectangle x1="-0.254" y1="3.683" x2="0.254" y2="3.937" layer="21"/>
<rectangle x1="-0.254" y1="1.143" x2="0.254" y2="1.397" layer="21"/>
<rectangle x1="2.286" y1="1.143" x2="2.794" y2="1.397" layer="21"/>
<rectangle x1="-0.254" y1="-1.397" x2="0.254" y2="-1.143" layer="21"/>
<rectangle x1="2.286" y1="-1.397" x2="2.794" y2="-1.143" layer="21"/>
<rectangle x1="-0.254" y1="-3.937" x2="0.254" y2="-3.683" layer="21"/>
<rectangle x1="2.286" y1="-3.937" x2="2.794" y2="-3.683" layer="21"/>
<rectangle x1="-0.254" y1="-6.477" x2="0.254" y2="-6.223" layer="21"/>
<rectangle x1="2.286" y1="-6.477" x2="2.794" y2="-6.223" layer="21"/>
<rectangle x1="-0.254" y1="-9.017" x2="0.254" y2="-8.763" layer="21"/>
<rectangle x1="2.286" y1="-9.017" x2="2.794" y2="-8.763" layer="21"/>
<wire x1="10.033" y1="8.89" x2="11.303" y2="9.652" width="0.127" layer="21"/>
<wire x1="11.303" y1="9.652" x2="11.303" y2="8.255" width="0.127" layer="21"/>
<wire x1="11.303" y1="8.255" x2="10.033" y2="8.89" width="0.127" layer="21"/>
</package>
</packages>
<symbols>
<symbol name="2X8">
<pin name="15" x="-12.7" y="-8.89" visible="pin" length="middle"/>
<pin name="13" x="-12.7" y="-6.35" visible="pin" length="middle"/>
<pin name="11" x="-12.7" y="-3.81" visible="pin" length="middle"/>
<pin name="9" x="-12.7" y="-1.27" visible="pin" length="middle"/>
<pin name="7" x="-12.7" y="1.27" visible="pin" length="middle"/>
<pin name="5" x="-12.7" y="3.81" visible="pin" length="middle"/>
<pin name="3" x="-12.7" y="6.35" visible="pin" length="middle"/>
<pin name="1" x="-12.7" y="8.89" visible="pin" length="middle"/>
<pin name="2" x="12.7" y="8.89" visible="pin" length="middle" rot="R180"/>
<pin name="4" x="12.7" y="6.35" visible="pin" length="middle" rot="R180"/>
<pin name="6" x="12.7" y="3.81" visible="pin" length="middle" rot="R180"/>
<pin name="8" x="12.7" y="1.27" visible="pin" length="middle" rot="R180"/>
<pin name="10" x="12.7" y="-1.27" visible="pin" length="middle" rot="R180"/>
<pin name="12" x="12.7" y="-3.81" visible="pin" length="middle" rot="R180"/>
<pin name="14" x="12.7" y="-6.35" visible="pin" length="middle" rot="R180"/>
<pin name="16" x="12.7" y="-8.89" visible="pin" length="middle" rot="R180"/>
<wire x1="-7.62" y1="11.43" x2="7.62" y2="11.43" width="0.254" layer="94"/>
<wire x1="7.62" y1="11.43" x2="7.62" y2="-11.43" width="0.254" layer="94"/>
<wire x1="7.62" y1="-11.43" x2="-7.62" y2="-11.43" width="0.254" layer="94"/>
<wire x1="-7.62" y1="-11.43" x2="-7.62" y2="11.43" width="0.254" layer="94"/>
<text x="-7.62" y="12.7" size="1.27" layer="95" font="vector">&gt;NAME</text>
<text x="-7.62" y="-13.97" size="1.27" layer="96" font="vector">&gt;VALUE</text>
</symbol>
</symbols>
<devicesets>
<deviceset name="2X8" prefix="CN" uservalue="yes">
<gates>
<gate name="G$1" symbol="2X8" x="0" y="0"/>
</gates>
<devices>
<device name="_STRAIGHT" package="2X8_100MIL">
<connects>
<connect gate="G$1" pin="1" pad="1"/>
<connect gate="G$1" pin="10" pad="10"/>
<connect gate="G$1" pin="11" pad="11"/>
<connect gate="G$1" pin="12" pad="12"/>
<connect gate="G$1" pin="13" pad="13"/>
<connect gate="G$1" pin="14" pad="14"/>
<connect gate="G$1" pin="15" pad="15"/>
<connect gate="G$1" pin="16" pad="16"/>
<connect gate="G$1" pin="2" pad="2"/>
<connect gate="G$1" pin="3" pad="3"/>
<connect gate="G$1" pin="4" pad="4"/>
<connect gate="G$1" pin="5" pad="5"/>
<connect gate="G$1" pin="6" pad="6"/>
<connect gate="G$1" pin="7" pad="7"/>
<connect gate="G$1" pin="8" pad="8"/>
<connect gate="G$1" pin="9" pad="9"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="_RIGHT_ANGLE" package="2X8_100MIL_R/A">
<connects>
<connect gate="G$1" pin="1" pad="1"/>
<connect gate="G$1" pin="10" pad="10"/>
<connect gate="G$1" pin="11" pad="11"/>
<connect gate="G$1" pin="12" pad="12"/>
<connect gate="G$1" pin="13" pad="13"/>
<connect gate="G$1" pin="14" pad="14"/>
<connect gate="G$1" pin="15" pad="15"/>
<connect gate="G$1" pin="16" pad="16"/>
<connect gate="G$1" pin="2" pad="2"/>
<connect gate="G$1" pin="3" pad="3"/>
<connect gate="G$1" pin="4" pad="4"/>
<connect gate="G$1" pin="5" pad="5"/>
<connect gate="G$1" pin="6" pad="6"/>
<connect gate="G$1" pin="7" pad="7"/>
<connect gate="G$1" pin="8" pad="8"/>
<connect gate="G$1" pin="9" pad="9"/>
</connects>
<technologies>
<technology name="">
<attribute name="MPN" value="" constant="no"/>
</technology>
</technologies>
</device>
</devices>
</deviceset>
</devicesets>
</library>
<library name="USER_MOLEX_CGRID_III">
<packages>
<package name="1X4_0901361204">
<pad name="2" x="1.27" y="0" drill="1"/>
<pad name="3" x="-1.27" y="0" drill="1"/>
<wire x1="5.52" y1="-3.5" x2="5.52" y2="3.5" width="0.1524" layer="21"/>
<wire x1="5.52" y1="3.5" x2="-5.52" y2="3.5" width="0.1524" layer="21"/>
<wire x1="-5.52" y1="3.5" x2="-5.52" y2="-3.5" width="0.1524" layer="21"/>
<wire x1="-5.52" y1="-3.5" x2="5.52" y2="-3.5" width="0.1524" layer="21"/>
<polygon width="0.1524" layer="21">
<vertex x="4.27" y="-4"/>
<vertex x="3.52" y="-5"/>
<vertex x="5.02" y="-5"/>
</polygon>
<text x="-4.25" y="-5" size="1" layer="25" font="vector">&gt;NAME</text>
<pad name="1" x="3.81" y="0" drill="1" shape="square"/>
<pad name="4" x="-3.81" y="0" drill="1"/>
</package>
</packages>
<symbols>
<symbol name="1X4_HEADER_C_GRID_3">
<pin name="1" x="-7.62" y="3.81" visible="pad" length="middle"/>
<pin name="3" x="-7.62" y="-1.27" visible="pad" length="middle"/>
<circle x="-1.905" y="3.81" radius="0.635" width="0.127" layer="94"/>
<circle x="-1.905" y="1.27" radius="0.635" width="0.127" layer="94"/>
<wire x1="-3.81" y1="6.35" x2="-3.81" y2="-6.35" width="0.254" layer="94"/>
<text x="-3.81" y="7.62" size="1.27" layer="95" font="vector">&gt;NAME</text>
<wire x1="1.27" y1="6.35" x2="-3.81" y2="6.35" width="0.254" layer="94"/>
<wire x1="-3.81" y1="-6.35" x2="1.27" y2="-6.35" width="0.254" layer="94"/>
<wire x1="1.27" y1="-6.35" x2="1.27" y2="6.35" width="0.254" layer="94"/>
<text x="-3.81" y="-8.89" size="1.27" layer="96" font="vector">&gt;VALUE</text>
<pin name="2" x="-7.62" y="1.27" visible="pad" length="middle"/>
<pin name="4" x="-7.62" y="-3.81" visible="pad" length="middle"/>
<circle x="-1.905" y="-1.27" radius="0.635" width="0.127" layer="94"/>
<circle x="-1.905" y="-3.81" radius="0.635" width="0.127" layer="94"/>
</symbol>
</symbols>
<devicesets>
<deviceset name="MOLEX_CGRID_III_0901361204" prefix="CN" uservalue="yes">
<gates>
<gate name="G$1" symbol="1X4_HEADER_C_GRID_3" x="0" y="0"/>
</gates>
<devices>
<device name="" package="1X4_0901361204">
<connects>
<connect gate="G$1" pin="1" pad="1"/>
<connect gate="G$1" pin="2" pad="2"/>
<connect gate="G$1" pin="3" pad="3"/>
<connect gate="G$1" pin="4" pad="4"/>
</connects>
<technologies>
<technology name="">
<attribute name="MPN" value="" constant="no"/>
</technology>
</technologies>
</device>
</devices>
</deviceset>
</devicesets>
</library>
<library name="USER_CIRCUIT_PROTECTION">
<packages>
<package name="LITTELFUSE_MINI_BLADE_HOLDER_01530009">
<hole x="0" y="0" drill="3.7846"/>
<pad name="1" x="-1.7272" y="-3.81" drill="1.27" diameter="2.54"/>
<pad name="2" x="1.7272" y="3.81" drill="1.27" diameter="2.54"/>
<wire x1="3.81" y1="-8.636" x2="3.81" y2="8.636" width="0.254" layer="21"/>
<wire x1="3.81" y1="8.636" x2="-3.81" y2="8.636" width="0.254" layer="21"/>
<wire x1="-3.81" y1="8.636" x2="-3.81" y2="-8.636" width="0.254" layer="21"/>
<wire x1="-3.81" y1="-8.636" x2="3.81" y2="-8.636" width="0.254" layer="21"/>
<text x="-3.81" y="-10.414" size="1.27" layer="25" font="vector">&gt;NAME</text>
</package>
</packages>
<symbols>
<symbol name="FUSE_HOLDER">
<pin name="IN" x="-10.16" y="0" visible="pin" length="short"/>
<pin name="OUT" x="10.16" y="0" visible="pin" length="short" rot="R180"/>
<wire x1="-7.62" y1="2.54" x2="-7.62" y2="-2.54" width="0.254" layer="94"/>
<wire x1="-7.62" y1="-2.54" x2="7.62" y2="-2.54" width="0.254" layer="94"/>
<wire x1="7.62" y1="-2.54" x2="7.62" y2="2.54" width="0.254" layer="94"/>
<wire x1="7.62" y1="2.54" x2="5.08" y2="2.54" width="0.254" layer="94"/>
<wire x1="5.08" y1="2.54" x2="-5.08" y2="2.54" width="0.254" layer="94"/>
<wire x1="-5.08" y1="2.54" x2="-7.62" y2="2.54" width="0.254" layer="94"/>
<wire x1="-5.08" y1="7.62" x2="-5.08" y2="2.54" width="0.254" layer="94"/>
<wire x1="-5.08" y1="7.62" x2="5.08" y2="7.62" width="0.254" layer="94"/>
<wire x1="5.08" y1="7.62" x2="5.08" y2="2.54" width="0.254" layer="94"/>
<wire x1="-2.54" y1="5.08" x2="0" y2="5.08" width="0.254" layer="94" curve="180"/>
<wire x1="0" y1="5.08" x2="2.54" y2="5.08" width="0.254" layer="94" curve="-180"/>
<circle x="-2.54" y="5.715" radius="0.635" width="0.254" layer="94"/>
<circle x="2.54" y="4.445" radius="0.635" width="0.254" layer="94"/>
<text x="-7.62" y="-5.08" size="1.27" layer="95" font="vector">&gt;NAME</text>
<text x="-7.62" y="-7.62" size="1.27" layer="96" font="vector">&gt;VALUE</text>
</symbol>
</symbols>
<devicesets>
<deviceset name="FUSE_HOLDER" prefix="F" uservalue="yes">
<gates>
<gate name="G$1" symbol="FUSE_HOLDER" x="0" y="0"/>
</gates>
<devices>
<device name="_AUTOMOTIVE_MINI_BLADE" package="LITTELFUSE_MINI_BLADE_HOLDER_01530009">
<connects>
<connect gate="G$1" pin="IN" pad="1"/>
<connect gate="G$1" pin="OUT" pad="2"/>
</connects>
<technologies>
<technology name="">
<attribute name="MPN" value="" constant="no"/>
</technology>
</technologies>
</device>
</devices>
</deviceset>
</devicesets>
</library>
</libraries>
<attributes>
<attribute name="DOC_NAME" value="LED STRING MANAGER"/>
<attribute name="DOC_NUMBER" value="N/A"/>
<attribute name="DOC_REVISION" value="1"/>
<attribute name="INITIALS_CHECKED" value=""/>
<attribute name="INITIALS_DRAWN" value="KJD"/>
</attributes>
<variantdefs>
</variantdefs>
<classes>
<class number="0" name="default" width="0" drill="0">
</class>
</classes>
<parts>
<part name="FRAME1" library="frames" library_urn="urn:adsk.eagle:library:229" deviceset="FRAME_A_L" device=""/>
<part name="U$1" library="USER_DOC FRAMES" deviceset="TITLE_BLOCK_GALOIS" device="">
<attribute name="DOC_NAME" value=""/>
<attribute name="DOC_NUMBER" value=""/>
<attribute name="DOC_REVISION" value=""/>
<attribute name="INITIALS_CHECKED" value=""/>
</part>
<part name="FRAME2" library="frames" library_urn="urn:adsk.eagle:library:229" deviceset="FRAME_A_L" device=""/>
<part name="U$2" library="USER_DOC FRAMES" deviceset="TITLE_BLOCK_GALOIS" device=""/>
<part name="GND1" library="supply1" library_urn="urn:adsk.eagle:library:371" deviceset="GND" device=""/>
<part name="J1" library="USER_CON_HIGH_CURRENT" deviceset="FASTON_PCB_THRU_R/A" device="" value="928814-1">
<attribute name="MPN" value="928814-1"/>
</part>
<part name="J2" library="USER_CON_HIGH_CURRENT" deviceset="FASTON_PCB_THRU_R/A" device="" value="928814-1">
<attribute name="MPN" value="928814-1"/>
</part>
<part name="R2" library="USER_SMT_CHIP_STANDARD" deviceset="R_SMD" device="R0603" value="4.99k">
<attribute name="MPN" value="ERJ-3EKF4991V"/>
</part>
<part name="C1" library="USER_SMT_CHIP_STANDARD" deviceset="C_SMD" device="C0603" value="0.1u">
<attribute name="MPN" value="CL10B104KB8NNNC"/>
</part>
<part name="U2" library="USER_SMART_SWITCHES" deviceset="ITS428L2" device="" value="ITS428L2">
<attribute name="MPN" value="ITS428L2ATMA1"/>
</part>
<part name="U1" library="USER_PMIC" deviceset="TPS3847" device="" value="TPS3847108">
<attribute name="MPN" value="TPS3847108DBVR"/>
</part>
<part name="D2" library="USER_SMT_CHIP_STANDARD" deviceset="LED_SMD" device="" value="GREEN">
<attribute name="MPN" value="LG Q396-PS-35"/>
</part>
<part name="J5" library="USER_CON_HIGH_CURRENT" deviceset="HPM_1X3_R/A" device="" value="HPM-03-02-T-S-RA">
<attribute name="MPN" value="HPM-03-02-T-S-RA"/>
</part>
<part name="U$4" library="USER_GALOIS_CYBERPHYS" deviceset="USB_RELAY_PCB_FOOTPRINT" device=""/>
<part name="C2" library="USER_CAPACITORS_ELECTROLYTIC" deviceset="C_POLARIZED" device="_DIA_12.5MM_LEADS_5MM" value="2200u">
<attribute name="MPN" value="EEU-HD1E222"/>
</part>
<part name="GND2" library="supply1" library_urn="urn:adsk.eagle:library:371" deviceset="GND" device=""/>
<part name="R1" library="USER_SMT_CHIP_STANDARD" deviceset="R_SMD" device="R0603" value="4.99k">
<attribute name="MPN" value="ERJ-3EKF4991V"/>
</part>
<part name="D1" library="USER_SMT_CHIP_STANDARD" deviceset="LED_SMD" device="" value="GREEN">
<attribute name="MPN" value="LG Q396-PS-35"/>
</part>
<part name="CN1" library="USER_CON_PINS" deviceset="2X8" device="_RIGHT_ANGLE" value="2X8_100MIL_R/A_RECEPTACLE">
<attribute name="MPN" value="PPPC082LJBN-RC"/>
</part>
<part name="GND3" library="supply1" library_urn="urn:adsk.eagle:library:371" deviceset="GND" device=""/>
<part name="CN2" library="USER_MOLEX_CGRID_III" deviceset="MOLEX_CGRID_III_0901361204" device="" value="1x4_100MIL_STRT_PINS">
<attribute name="MPN" value="0901361204"/>
</part>
<part name="CN3" library="USER_MOLEX_CGRID_III" deviceset="MOLEX_CGRID_III_0901361204" device="" value="1x4_100MIL_STRT_PINS">
<attribute name="MPN" value="0901361204"/>
</part>
<part name="CN4" library="USER_MOLEX_CGRID_III" deviceset="MOLEX_CGRID_III_0901361204" device="" value="1x4_100MIL_STRT_PINS">
<attribute name="MPN" value="0901361204"/>
</part>
<part name="CN5" library="USER_MOLEX_CGRID_III" deviceset="MOLEX_CGRID_III_0901361204" device="" value="1x4_100MIL_STRT_PINS">
<attribute name="MPN" value="0901361204"/>
</part>
<part name="CN6" library="USER_MOLEX_CGRID_III" deviceset="MOLEX_CGRID_III_0901361204" device="" value="1x4_100MIL_STRT_PINS">
<attribute name="MPN" value="0901361204"/>
</part>
<part name="CN7" library="USER_MOLEX_CGRID_III" deviceset="MOLEX_CGRID_III_0901361204" device="" value="1x4_100MIL_STRT_PINS">
<attribute name="MPN" value="0901361204"/>
</part>
<part name="CN8" library="USER_MOLEX_CGRID_III" deviceset="MOLEX_CGRID_III_0901361204" device="" value="1x4_100MIL_STRT_PINS">
<attribute name="MPN" value="0901361204"/>
</part>
<part name="CN9" library="USER_MOLEX_CGRID_III" deviceset="MOLEX_CGRID_III_0901361204" device="" value="1x4_100MIL_STRT_PINS">
<attribute name="MPN" value="0901361204"/>
</part>
<part name="GND4" library="supply1" library_urn="urn:adsk.eagle:library:371" deviceset="GND" device=""/>
<part name="GND5" library="supply1" library_urn="urn:adsk.eagle:library:371" deviceset="GND" device=""/>
<part name="GND6" library="supply1" library_urn="urn:adsk.eagle:library:371" deviceset="GND" device=""/>
<part name="GND7" library="supply1" library_urn="urn:adsk.eagle:library:371" deviceset="GND" device=""/>
<part name="GND8" library="supply1" library_urn="urn:adsk.eagle:library:371" deviceset="GND" device=""/>
<part name="GND9" library="supply1" library_urn="urn:adsk.eagle:library:371" deviceset="GND" device=""/>
<part name="GND10" library="supply1" library_urn="urn:adsk.eagle:library:371" deviceset="GND" device=""/>
<part name="GND11" library="supply1" library_urn="urn:adsk.eagle:library:371" deviceset="GND" device=""/>
<part name="U$3" library="USER_GALOIS_CYBERPHYS" deviceset="FADECANDY_PCB_FOOTPRINT" device=""/>
<part name="F1" library="USER_CIRCUIT_PROTECTION" deviceset="FUSE_HOLDER" device="_AUTOMOTIVE_MINI_BLADE" value="01530009Z">
<attribute name="MPN" value="01530009Z"/>
</part>
</parts>
<sheets>
<sheet>
<plain>
<text x="12.7" y="196.85" size="6.35" layer="97">FADECANDY INTERFACE</text>
<text x="12.7" y="190.5" size="3.175" layer="97" font="vector">WITH LED STRING HEADERS</text>
<text x="171.45" y="17.78" size="2.54" layer="94" font="vector">KJD</text>
<text x="171.45" y="25.4" size="2.54" layer="94">&gt;DOC_NAME</text>
<text x="233.68" y="25.4" size="2.54" layer="94">&gt;DOC_NUMBER</text>
<text x="260.35" y="25.4" size="2.54" layer="94">&gt;DOC_REVISION</text>
</plain>
<instances>
<instance part="FRAME1" gate="G$1" x="0" y="0" smashed="yes"/>
<instance part="U$1" gate="G$1" x="168.91" y="0" smashed="yes">
<attribute name="SHEET" x="260.35" y="17.78" size="2.54" layer="94" font="vector"/>
<attribute name="LAST_DATE_TIME" x="201.93" y="17.78" size="2.54" layer="94" font="vector"/>
<attribute name="DOC_NAME" x="171.45" y="25.4" size="2.54" layer="94" font="vector"/>
<attribute name="DOC_NUMBER" x="233.68" y="25.4" size="2.54" layer="94" font="vector"/>
<attribute name="DOC_REVISION" x="260.35" y="25.4" size="2.54" layer="94" font="vector"/>
<attribute name="INITIALS_CHECKED" x="186.69" y="17.78" size="2.54" layer="94" font="vector"/>
</instance>
<instance part="CN1" gate="G$1" x="38.1" y="114.3" smashed="yes" rot="MR0">
<attribute name="NAME" x="30.48" y="127" size="1.27" layer="95" font="vector"/>
<attribute name="VALUE" x="30.48" y="100.33" size="1.27" layer="96" font="vector"/>
</instance>
<instance part="GND3" gate="1" x="22.86" y="100.33" smashed="yes">
<attribute name="VALUE" x="22.86" y="97.79" size="1.778" layer="96" align="bottom-center"/>
</instance>
<instance part="CN2" gate="G$1" x="101.6" y="76.2" smashed="yes">
<attribute name="NAME" x="97.79" y="83.82" size="1.27" layer="95" font="vector"/>
<attribute name="VALUE" x="97.79" y="67.31" size="1.27" layer="96" font="vector"/>
</instance>
<instance part="CN3" gate="G$1" x="152.4" y="76.2" smashed="yes">
<attribute name="NAME" x="148.59" y="83.82" size="1.27" layer="95" font="vector"/>
<attribute name="VALUE" x="148.59" y="67.31" size="1.27" layer="96" font="vector"/>
</instance>
<instance part="CN4" gate="G$1" x="203.2" y="76.2" smashed="yes">
<attribute name="NAME" x="199.39" y="83.82" size="1.27" layer="95" font="vector"/>
<attribute name="VALUE" x="199.39" y="67.31" size="1.27" layer="96" font="vector"/>
</instance>
<instance part="CN5" gate="G$1" x="254" y="76.2" smashed="yes">
<attribute name="NAME" x="250.19" y="83.82" size="1.27" layer="95" font="vector"/>
<attribute name="VALUE" x="250.19" y="67.31" size="1.27" layer="96" font="vector"/>
</instance>
<instance part="CN6" gate="G$1" x="101.6" y="152.4" smashed="yes">
<attribute name="NAME" x="97.79" y="160.02" size="1.27" layer="95" font="vector"/>
<attribute name="VALUE" x="97.79" y="143.51" size="1.27" layer="96" font="vector"/>
</instance>
<instance part="CN7" gate="G$1" x="152.4" y="152.4" smashed="yes">
<attribute name="NAME" x="148.59" y="160.02" size="1.27" layer="95" font="vector"/>
<attribute name="VALUE" x="148.59" y="143.51" size="1.27" layer="96" font="vector"/>
</instance>
<instance part="CN8" gate="G$1" x="203.2" y="152.4" smashed="yes">
<attribute name="NAME" x="199.39" y="160.02" size="1.27" layer="95" font="vector"/>
<attribute name="VALUE" x="199.39" y="143.51" size="1.27" layer="96" font="vector"/>
</instance>
<instance part="CN9" gate="G$1" x="254" y="152.4" smashed="yes">
<attribute name="NAME" x="250.19" y="160.02" size="1.27" layer="95" font="vector"/>
<attribute name="VALUE" x="250.19" y="143.51" size="1.27" layer="96" font="vector"/>
</instance>
<instance part="GND4" gate="1" x="91.44" y="143.51" smashed="yes">
<attribute name="VALUE" x="91.44" y="140.97" size="1.778" layer="96" align="bottom-center"/>
</instance>
<instance part="GND5" gate="1" x="142.24" y="143.51" smashed="yes">
<attribute name="VALUE" x="142.24" y="140.97" size="1.778" layer="96" align="bottom-center"/>
</instance>
<instance part="GND6" gate="1" x="193.04" y="143.51" smashed="yes">
<attribute name="VALUE" x="193.04" y="140.97" size="1.778" layer="96" align="bottom-center"/>
</instance>
<instance part="GND7" gate="1" x="243.84" y="143.51" smashed="yes">
<attribute name="VALUE" x="243.84" y="140.97" size="1.778" layer="96" align="bottom-center"/>
</instance>
<instance part="GND8" gate="1" x="91.44" y="67.31" smashed="yes">
<attribute name="VALUE" x="91.44" y="64.77" size="1.778" layer="96" align="bottom-center"/>
</instance>
<instance part="GND9" gate="1" x="142.24" y="67.31" smashed="yes">
<attribute name="VALUE" x="142.24" y="64.77" size="1.778" layer="96" align="bottom-center"/>
</instance>
<instance part="GND10" gate="1" x="193.04" y="67.31" smashed="yes">
<attribute name="VALUE" x="193.04" y="64.77" size="1.778" layer="96" align="bottom-center"/>
</instance>
<instance part="GND11" gate="1" x="243.84" y="67.31" smashed="yes">
<attribute name="VALUE" x="243.84" y="64.77" size="1.778" layer="96" align="bottom-center"/>
</instance>
<instance part="U$3" gate="G$1" x="38.1" y="146.05" smashed="yes"/>
</instances>
<busses>
</busses>
<nets>
<net name="GND" class="0">
<segment>
<pinref part="CN1" gate="G$1" pin="16"/>
<wire x1="25.4" y1="105.41" x2="22.86" y2="105.41" width="0.1524" layer="91"/>
<pinref part="CN1" gate="G$1" pin="2"/>
<wire x1="22.86" y1="105.41" x2="22.86" y2="107.95" width="0.1524" layer="91"/>
<wire x1="22.86" y1="107.95" x2="22.86" y2="110.49" width="0.1524" layer="91"/>
<wire x1="22.86" y1="110.49" x2="22.86" y2="113.03" width="0.1524" layer="91"/>
<wire x1="22.86" y1="113.03" x2="22.86" y2="115.57" width="0.1524" layer="91"/>
<wire x1="22.86" y1="115.57" x2="22.86" y2="118.11" width="0.1524" layer="91"/>
<wire x1="22.86" y1="118.11" x2="22.86" y2="120.65" width="0.1524" layer="91"/>
<wire x1="22.86" y1="120.65" x2="22.86" y2="123.19" width="0.1524" layer="91"/>
<wire x1="22.86" y1="123.19" x2="25.4" y2="123.19" width="0.1524" layer="91"/>
<pinref part="CN1" gate="G$1" pin="4"/>
<wire x1="25.4" y1="120.65" x2="22.86" y2="120.65" width="0.1524" layer="91"/>
<junction x="22.86" y="120.65"/>
<pinref part="CN1" gate="G$1" pin="6"/>
<wire x1="25.4" y1="118.11" x2="22.86" y2="118.11" width="0.1524" layer="91"/>
<junction x="22.86" y="118.11"/>
<pinref part="CN1" gate="G$1" pin="8"/>
<wire x1="25.4" y1="115.57" x2="22.86" y2="115.57" width="0.1524" layer="91"/>
<junction x="22.86" y="115.57"/>
<pinref part="CN1" gate="G$1" pin="10"/>
<wire x1="25.4" y1="113.03" x2="22.86" y2="113.03" width="0.1524" layer="91"/>
<junction x="22.86" y="113.03"/>
<pinref part="CN1" gate="G$1" pin="12"/>
<wire x1="25.4" y1="110.49" x2="22.86" y2="110.49" width="0.1524" layer="91"/>
<junction x="22.86" y="110.49"/>
<pinref part="CN1" gate="G$1" pin="14"/>
<wire x1="25.4" y1="107.95" x2="22.86" y2="107.95" width="0.1524" layer="91"/>
<junction x="22.86" y="107.95"/>
<pinref part="GND3" gate="1" pin="GND"/>
<wire x1="22.86" y1="102.87" x2="22.86" y2="105.41" width="0.1524" layer="91"/>
<junction x="22.86" y="105.41"/>
</segment>
<segment>
<pinref part="CN6" gate="G$1" pin="4"/>
<wire x1="93.98" y1="148.59" x2="91.44" y2="148.59" width="0.1524" layer="91"/>
<pinref part="GND4" gate="1" pin="GND"/>
<wire x1="91.44" y1="148.59" x2="91.44" y2="146.05" width="0.1524" layer="91"/>
</segment>
<segment>
<pinref part="GND7" gate="1" pin="GND"/>
<wire x1="243.84" y1="146.05" x2="243.84" y2="148.59" width="0.1524" layer="91"/>
<pinref part="CN9" gate="G$1" pin="4"/>
<wire x1="243.84" y1="148.59" x2="246.38" y2="148.59" width="0.1524" layer="91"/>
</segment>
<segment>
<pinref part="GND6" gate="1" pin="GND"/>
<wire x1="193.04" y1="146.05" x2="193.04" y2="148.59" width="0.1524" layer="91"/>
<pinref part="CN8" gate="G$1" pin="4"/>
<wire x1="193.04" y1="148.59" x2="195.58" y2="148.59" width="0.1524" layer="91"/>
</segment>
<segment>
<pinref part="GND5" gate="1" pin="GND"/>
<wire x1="142.24" y1="146.05" x2="142.24" y2="148.59" width="0.1524" layer="91"/>
<pinref part="CN7" gate="G$1" pin="4"/>
<wire x1="142.24" y1="148.59" x2="144.78" y2="148.59" width="0.1524" layer="91"/>
</segment>
<segment>
<pinref part="GND11" gate="1" pin="GND"/>
<pinref part="CN5" gate="G$1" pin="4"/>
<wire x1="243.84" y1="69.85" x2="243.84" y2="72.39" width="0.1524" layer="91"/>
<wire x1="243.84" y1="72.39" x2="246.38" y2="72.39" width="0.1524" layer="91"/>
</segment>
<segment>
<pinref part="GND10" gate="1" pin="GND"/>
<pinref part="CN4" gate="G$1" pin="4"/>
<wire x1="193.04" y1="69.85" x2="193.04" y2="72.39" width="0.1524" layer="91"/>
<wire x1="193.04" y1="72.39" x2="195.58" y2="72.39" width="0.1524" layer="91"/>
</segment>
<segment>
<pinref part="GND9" gate="1" pin="GND"/>
<pinref part="CN3" gate="G$1" pin="4"/>
<wire x1="142.24" y1="69.85" x2="142.24" y2="72.39" width="0.1524" layer="91"/>
<wire x1="142.24" y1="72.39" x2="144.78" y2="72.39" width="0.1524" layer="91"/>
</segment>
<segment>
<pinref part="GND8" gate="1" pin="GND"/>
<pinref part="CN2" gate="G$1" pin="4"/>
<wire x1="91.44" y1="69.85" x2="91.44" y2="72.39" width="0.1524" layer="91"/>
<wire x1="91.44" y1="72.39" x2="93.98" y2="72.39" width="0.1524" layer="91"/>
</segment>
</net>
<net name="LED_STRING_7" class="0">
<segment>
<pinref part="CN1" gate="G$1" pin="1"/>
<wire x1="50.8" y1="123.19" x2="68.58" y2="123.19" width="0.1524" layer="91"/>
<wire x1="68.58" y1="123.19" x2="68.58" y2="151.13" width="0.1524" layer="91"/>
<pinref part="CN6" gate="G$1" pin="3"/>
<wire x1="68.58" y1="151.13" x2="93.98" y2="151.13" width="0.1524" layer="91"/>
<label x="52.07" y="123.19" size="1.27" layer="95"/>
<label x="92.71" y="151.13" size="1.27" layer="95" rot="MR0"/>
</segment>
</net>
<net name="LED_STRING_6" class="0">
<segment>
<pinref part="CN1" gate="G$1" pin="3"/>
<wire x1="50.8" y1="120.65" x2="121.92" y2="120.65" width="0.1524" layer="91"/>
<wire x1="121.92" y1="120.65" x2="121.92" y2="151.13" width="0.1524" layer="91"/>
<pinref part="CN7" gate="G$1" pin="3"/>
<wire x1="121.92" y1="151.13" x2="144.78" y2="151.13" width="0.1524" layer="91"/>
<label x="52.07" y="120.65" size="1.27" layer="95"/>
<label x="143.51" y="151.13" size="1.27" layer="95" rot="MR0"/>
</segment>
</net>
<net name="LED_STRING_5" class="0">
<segment>
<pinref part="CN1" gate="G$1" pin="5"/>
<wire x1="50.8" y1="118.11" x2="172.72" y2="118.11" width="0.1524" layer="91"/>
<wire x1="172.72" y1="118.11" x2="172.72" y2="151.13" width="0.1524" layer="91"/>
<pinref part="CN8" gate="G$1" pin="3"/>
<wire x1="172.72" y1="151.13" x2="195.58" y2="151.13" width="0.1524" layer="91"/>
<label x="52.07" y="118.11" size="1.27" layer="95"/>
<label x="194.31" y="151.13" size="1.27" layer="95" rot="MR0"/>
</segment>
</net>
<net name="LED_STRING_4" class="0">
<segment>
<pinref part="CN1" gate="G$1" pin="7"/>
<wire x1="50.8" y1="115.57" x2="223.52" y2="115.57" width="0.1524" layer="91"/>
<wire x1="223.52" y1="115.57" x2="223.52" y2="151.13" width="0.1524" layer="91"/>
<pinref part="CN9" gate="G$1" pin="3"/>
<wire x1="223.52" y1="151.13" x2="246.38" y2="151.13" width="0.1524" layer="91"/>
<label x="52.07" y="115.57" size="1.27" layer="95"/>
<label x="245.11" y="151.13" size="1.27" layer="95" rot="MR0"/>
</segment>
</net>
<net name="LED_STRING_3" class="0">
<segment>
<pinref part="CN1" gate="G$1" pin="9"/>
<wire x1="50.8" y1="113.03" x2="223.52" y2="113.03" width="0.1524" layer="91"/>
<pinref part="CN5" gate="G$1" pin="3"/>
<wire x1="223.52" y1="113.03" x2="223.52" y2="74.93" width="0.1524" layer="91"/>
<wire x1="223.52" y1="74.93" x2="246.38" y2="74.93" width="0.1524" layer="91"/>
<label x="52.07" y="113.03" size="1.27" layer="95"/>
<label x="245.11" y="74.93" size="1.27" layer="95" rot="MR0"/>
</segment>
</net>
<net name="LED_STRING_2" class="0">
<segment>
<pinref part="CN1" gate="G$1" pin="11"/>
<wire x1="50.8" y1="110.49" x2="172.72" y2="110.49" width="0.1524" layer="91"/>
<pinref part="CN4" gate="G$1" pin="3"/>
<wire x1="172.72" y1="110.49" x2="172.72" y2="74.93" width="0.1524" layer="91"/>
<wire x1="172.72" y1="74.93" x2="195.58" y2="74.93" width="0.1524" layer="91"/>
<label x="52.07" y="110.49" size="1.27" layer="95"/>
<label x="194.31" y="74.93" size="1.27" layer="95" rot="MR0"/>
</segment>
</net>
<net name="LED_STRING_1" class="0">
<segment>
<pinref part="CN1" gate="G$1" pin="13"/>
<wire x1="50.8" y1="107.95" x2="121.92" y2="107.95" width="0.1524" layer="91"/>
<pinref part="CN3" gate="G$1" pin="3"/>
<wire x1="121.92" y1="107.95" x2="121.92" y2="74.93" width="0.1524" layer="91"/>
<wire x1="121.92" y1="74.93" x2="144.78" y2="74.93" width="0.1524" layer="91"/>
<label x="52.07" y="107.95" size="1.27" layer="95"/>
<label x="143.51" y="74.93" size="1.27" layer="95" rot="MR0"/>
</segment>
</net>
<net name="LED_STRING_0" class="0">
<segment>
<pinref part="CN1" gate="G$1" pin="15"/>
<wire x1="50.8" y1="105.41" x2="68.58" y2="105.41" width="0.1524" layer="91"/>
<pinref part="CN2" gate="G$1" pin="3"/>
<wire x1="68.58" y1="105.41" x2="68.58" y2="74.93" width="0.1524" layer="91"/>
<wire x1="68.58" y1="74.93" x2="93.98" y2="74.93" width="0.1524" layer="91"/>
<label x="52.07" y="105.41" size="1.27" layer="95"/>
<label x="92.71" y="74.93" size="1.27" layer="95" rot="MR0"/>
</segment>
</net>
<net name="VLED_+12V" class="0">
<segment>
<pinref part="CN6" gate="G$1" pin="1"/>
<wire x1="93.98" y1="156.21" x2="91.44" y2="156.21" width="0.1524" layer="91"/>
<label x="91.44" y="156.21" size="1.27" layer="95" rot="R180" xref="yes"/>
</segment>
<segment>
<pinref part="CN7" gate="G$1" pin="1"/>
<wire x1="144.78" y1="156.21" x2="142.24" y2="156.21" width="0.1524" layer="91"/>
<label x="142.24" y="156.21" size="1.27" layer="95" rot="R180" xref="yes"/>
</segment>
<segment>
<pinref part="CN8" gate="G$1" pin="1"/>
<wire x1="195.58" y1="156.21" x2="193.04" y2="156.21" width="0.1524" layer="91"/>
<label x="193.04" y="156.21" size="1.27" layer="95" rot="R180" xref="yes"/>
</segment>
<segment>
<pinref part="CN9" gate="G$1" pin="1"/>
<wire x1="246.38" y1="156.21" x2="243.84" y2="156.21" width="0.1524" layer="91"/>
<label x="243.84" y="156.21" size="1.27" layer="95" rot="R180" xref="yes"/>
</segment>
<segment>
<pinref part="CN2" gate="G$1" pin="1"/>
<wire x1="93.98" y1="80.01" x2="91.44" y2="80.01" width="0.1524" layer="91"/>
<label x="91.44" y="80.01" size="1.27" layer="95" rot="R180" xref="yes"/>
</segment>
<segment>
<pinref part="CN3" gate="G$1" pin="1"/>
<wire x1="144.78" y1="80.01" x2="142.24" y2="80.01" width="0.1524" layer="91"/>
<label x="142.24" y="80.01" size="1.27" layer="95" rot="R180" xref="yes"/>
</segment>
<segment>
<pinref part="CN4" gate="G$1" pin="1"/>
<wire x1="195.58" y1="80.01" x2="193.04" y2="80.01" width="0.1524" layer="91"/>
<label x="193.04" y="80.01" size="1.27" layer="95" rot="R180" xref="yes"/>
</segment>
<segment>
<pinref part="CN5" gate="G$1" pin="1"/>
<wire x1="246.38" y1="80.01" x2="243.84" y2="80.01" width="0.1524" layer="91"/>
<label x="243.84" y="80.01" size="1.27" layer="95" rot="R180" xref="yes"/>
</segment>
</net>
</nets>
</sheet>
<sheet>
<plain>
<text x="12.7" y="196.85" size="6.35" layer="97">USB RELAY INTERFACE</text>
<text x="12.7" y="190.5" size="3.175" layer="97">WITH CONTACT BOUNCE ELIMINATOR</text>
</plain>
<instances>
<instance part="FRAME2" gate="G$1" x="0" y="0" smashed="yes"/>
<instance part="U$2" gate="G$1" x="168.91" y="0" smashed="yes">
<attribute name="DOC_NAME" x="171.45" y="25.4" size="2.54" layer="94" font="vector"/>
<attribute name="DOC_NUMBER" x="233.68" y="25.4" size="2.54" layer="94" font="vector"/>
<attribute name="DOC_REVISION" x="260.35" y="25.4" size="2.54" layer="94" font="vector"/>
<attribute name="INITIALS_DRAWN" x="171.45" y="17.78" size="2.54" layer="94" font="vector"/>
<attribute name="INITIALS_CHECKED" x="186.69" y="17.78" size="2.54" layer="94" font="vector"/>
<attribute name="SHEET" x="260.35" y="17.78" size="2.54" layer="94" font="vector"/>
<attribute name="LAST_DATE_TIME" x="201.93" y="17.78" size="2.54" layer="94" font="vector"/>
</instance>
<instance part="GND1" gate="1" x="177.8" y="76.2" smashed="yes">
<attribute name="VALUE" x="177.8" y="73.66" size="1.778" layer="96" align="bottom-center"/>
</instance>
<instance part="J1" gate="G$1" x="38.1" y="162.56" smashed="yes" rot="MR0">
<attribute name="NAME" x="40.64" y="168.91" size="1.27" layer="95" font="vector" rot="MR0"/>
<attribute name="VALUE" x="40.64" y="166.37" size="1.27" layer="96" font="vector" rot="MR0"/>
</instance>
<instance part="J2" gate="G$1" x="38.1" y="88.9" smashed="yes" rot="MR0">
<attribute name="NAME" x="40.64" y="95.25" size="1.27" layer="95" font="vector" rot="MR0"/>
<attribute name="VALUE" x="40.64" y="92.71" size="1.27" layer="96" font="vector" rot="MR0"/>
</instance>
<instance part="R2" gate="G$1" x="227.33" y="113.03" smashed="yes" rot="R90">
<attribute name="NAME" x="229.87" y="114.3" size="1.27" layer="95" font="vector"/>
<attribute name="VALUE" x="229.87" y="111.76" size="1.27" layer="96" font="vector"/>
</instance>
<instance part="C1" gate="G$1" x="128.27" y="127" smashed="yes">
<attribute name="NAME" x="127" y="129.54" size="1.27" layer="95" font="vector"/>
<attribute name="VALUE" x="127" y="123.19" size="1.27" layer="96" font="vector"/>
<attribute name="PACKAGE" x="127" y="120.65" size="1.27" layer="97" font="vector" display="off"/>
</instance>
<instance part="U2" gate="G$1" x="177.8" y="110.49" smashed="yes">
<attribute name="NAME" x="167.64" y="119.38" size="1.27" layer="95" font="vector"/>
<attribute name="VALUE" x="167.64" y="100.33" size="1.27" layer="96" font="vector"/>
</instance>
<instance part="U1" gate="G$1" x="137.16" y="107.95" smashed="yes">
<attribute name="NAME" x="127" y="119.38" size="1.27" layer="95" font="vector"/>
<attribute name="VALUE" x="139.7" y="95.25" size="1.27" layer="96" font="vector"/>
</instance>
<instance part="D2" gate="G$1" x="227.33" y="100.33" smashed="yes" rot="R270">
<attribute name="NAME" x="232.41" y="101.6" size="1.27" layer="95" font="vector"/>
<attribute name="VALUE" x="232.41" y="99.06" size="1.27" layer="96" font="vector"/>
</instance>
<instance part="J5" gate="G$1" x="83.82" y="111.76" smashed="yes" rot="MR0">
<attribute name="NAME" x="86.36" y="120.65" size="1.27" layer="95" font="vector" rot="MR0"/>
<attribute name="VALUE" x="91.44" y="101.6" size="1.27" layer="96" font="vector" rot="MR0"/>
</instance>
<instance part="U$4" gate="G$1" x="58.42" y="111.76" smashed="yes"/>
<instance part="C2" gate="G$1" x="68.58" y="137.16" smashed="yes">
<attribute name="NAME" x="72.39" y="138.43" size="1.27" layer="95" font="vector"/>
<attribute name="VALUE" x="72.39" y="135.89" size="1.27" layer="96" font="vector"/>
</instance>
<instance part="GND2" gate="1" x="68.58" y="127" smashed="yes">
<attribute name="VALUE" x="68.58" y="124.46" size="1.778" layer="96" align="bottom-center"/>
</instance>
<instance part="R1" gate="G$1" x="95.25" y="132.08" smashed="yes">
<attribute name="NAME" x="93.98" y="134.62" size="1.27" layer="95" font="vector"/>
<attribute name="VALUE" x="93.98" y="129.54" size="1.27" layer="96" font="vector"/>
</instance>
<instance part="D1" gate="G$1" x="82.55" y="132.08" smashed="yes" rot="R180">
<attribute name="NAME" x="81.28" y="134.62" size="1.27" layer="95" font="vector"/>
<attribute name="VALUE" x="81.28" y="127" size="1.27" layer="96" font="vector"/>
</instance>
<instance part="F1" gate="G$1" x="54.61" y="143.51" smashed="yes">
<attribute name="NAME" x="46.99" y="138.43" size="1.27" layer="95" font="vector"/>
<attribute name="VALUE" x="46.99" y="135.89" size="1.27" layer="96" font="vector"/>
</instance>
</instances>
<busses>
</busses>
<nets>
<net name="GND" class="0">
<segment>
<wire x1="35.56" y1="82.55" x2="40.64" y2="82.55" width="0.1524" layer="91"/>
<pinref part="GND1" gate="1" pin="GND"/>
<wire x1="40.64" y1="82.55" x2="115.57" y2="82.55" width="0.1524" layer="91"/>
<wire x1="115.57" y1="82.55" x2="137.16" y2="82.55" width="0.1524" layer="91"/>
<wire x1="137.16" y1="82.55" x2="177.8" y2="82.55" width="0.1524" layer="91"/>
<wire x1="177.8" y1="82.55" x2="227.33" y2="82.55" width="0.1524" layer="91"/>
<wire x1="227.33" y1="82.55" x2="246.38" y2="82.55" width="0.1524" layer="91"/>
<wire x1="177.8" y1="78.74" x2="177.8" y2="82.55" width="0.1524" layer="91"/>
<junction x="177.8" y="82.55"/>
<pinref part="J2" gate="G$1" pin="2"/>
<wire x1="35.56" y1="83.82" x2="35.56" y2="82.55" width="0.1524" layer="91"/>
<pinref part="J2" gate="G$1" pin="1"/>
<wire x1="40.64" y1="83.82" x2="40.64" y2="82.55" width="0.1524" layer="91"/>
<junction x="40.64" y="82.55"/>
<label x="43.18" y="82.55" size="1.27" layer="95"/>
<wire x1="227.33" y1="96.52" x2="227.33" y2="82.55" width="0.1524" layer="91"/>
<junction x="227.33" y="82.55"/>
<pinref part="U2" gate="G$1" pin="GND"/>
<wire x1="177.8" y1="97.79" x2="177.8" y2="82.55" width="0.1524" layer="91"/>
<pinref part="U1" gate="G$1" pin="GND"/>
<wire x1="137.16" y1="92.71" x2="137.16" y2="82.55" width="0.1524" layer="91"/>
<junction x="137.16" y="82.55"/>
<pinref part="C1" gate="G$1" pin="P$1"/>
<wire x1="125.73" y1="127" x2="115.57" y2="127" width="0.1524" layer="91"/>
<wire x1="115.57" y1="127" x2="115.57" y2="82.55" width="0.1524" layer="91"/>
<junction x="115.57" y="82.55"/>
<pinref part="D2" gate="G$1" pin="C"/>
<label x="246.38" y="82.55" size="1.27" layer="95" xref="yes"/>
</segment>
<segment>
<pinref part="GND2" gate="1" pin="GND"/>
<pinref part="C2" gate="G$1" pin="C-"/>
<wire x1="68.58" y1="129.54" x2="68.58" y2="132.08" width="0.1524" layer="91"/>
<pinref part="D1" gate="G$1" pin="C"/>
<wire x1="68.58" y1="132.08" x2="68.58" y2="134.62" width="0.1524" layer="91"/>
<wire x1="78.74" y1="132.08" x2="68.58" y2="132.08" width="0.1524" layer="91"/>
<junction x="68.58" y="132.08"/>
</segment>
</net>
<net name="RELAY_OUT_+12V" class="0">
<segment>
<pinref part="U2" gate="G$1" pin="VBB"/>
<wire x1="193.04" y1="115.57" x2="212.09" y2="115.57" width="0.1524" layer="91"/>
<wire x1="212.09" y1="115.57" x2="212.09" y2="133.35" width="0.1524" layer="91"/>
<wire x1="212.09" y1="133.35" x2="137.16" y2="133.35" width="0.1524" layer="91"/>
<label x="195.58" y="115.57" size="1.27" layer="95"/>
<pinref part="U1" gate="G$1" pin="VCC"/>
<wire x1="137.16" y1="133.35" x2="120.65" y2="133.35" width="0.1524" layer="91"/>
<wire x1="137.16" y1="123.19" x2="137.16" y2="127" width="0.1524" layer="91"/>
<junction x="137.16" y="133.35"/>
<pinref part="C1" gate="G$1" pin="P$2"/>
<wire x1="137.16" y1="127" x2="137.16" y2="133.35" width="0.1524" layer="91"/>
<wire x1="132.08" y1="127" x2="137.16" y2="127" width="0.1524" layer="91"/>
<junction x="137.16" y="127"/>
<pinref part="U1" gate="G$1" pin="!MR"/>
<wire x1="121.92" y1="107.95" x2="120.65" y2="107.95" width="0.1524" layer="91"/>
<wire x1="120.65" y1="107.95" x2="120.65" y2="133.35" width="0.1524" layer="91"/>
<pinref part="J5" gate="G$1" pin="3"/>
<wire x1="91.44" y1="106.68" x2="110.49" y2="106.68" width="0.1524" layer="91"/>
<wire x1="110.49" y1="106.68" x2="110.49" y2="133.35" width="0.1524" layer="91"/>
<wire x1="110.49" y1="133.35" x2="120.65" y2="133.35" width="0.1524" layer="91"/>
<junction x="120.65" y="133.35"/>
<label x="92.71" y="106.68" size="1.27" layer="95"/>
</segment>
</net>
<net name="VLED_+12V" class="0">
<segment>
<wire x1="246.38" y1="133.35" x2="227.33" y2="133.35" width="0.1524" layer="91"/>
<pinref part="R2" gate="G$1" pin="P$2"/>
<wire x1="227.33" y1="116.84" x2="227.33" y2="133.35" width="0.1524" layer="91"/>
<junction x="227.33" y="133.35"/>
<pinref part="U2" gate="G$1" pin="VOUT"/>
<wire x1="193.04" y1="105.41" x2="217.17" y2="105.41" width="0.1524" layer="91"/>
<wire x1="217.17" y1="105.41" x2="217.17" y2="133.35" width="0.1524" layer="91"/>
<wire x1="217.17" y1="133.35" x2="227.33" y2="133.35" width="0.1524" layer="91"/>
<label x="195.58" y="105.41" size="1.27" layer="95"/>
<label x="246.38" y="133.35" size="1.27" layer="95" xref="yes"/>
</segment>
</net>
<net name="N$1" class="0">
<segment>
<pinref part="R2" gate="G$1" pin="P$1"/>
<wire x1="227.33" y1="110.49" x2="227.33" y2="104.14" width="0.1524" layer="91"/>
<pinref part="D2" gate="G$1" pin="A"/>
</segment>
</net>
<net name="N$3" class="0">
<segment>
<pinref part="U2" gate="G$1" pin="IN"/>
<wire x1="162.56" y1="115.57" x2="157.48" y2="115.57" width="0.1524" layer="91"/>
<wire x1="157.48" y1="115.57" x2="157.48" y2="107.95" width="0.1524" layer="91"/>
<pinref part="U1" gate="G$1" pin="!RST"/>
<wire x1="157.48" y1="107.95" x2="152.4" y2="107.95" width="0.1524" layer="91"/>
</segment>
</net>
<net name="FUSED_+12V" class="0">
<segment>
<pinref part="J5" gate="G$1" pin="2"/>
<wire x1="91.44" y1="111.76" x2="101.6" y2="111.76" width="0.1524" layer="91"/>
<wire x1="101.6" y1="111.76" x2="101.6" y2="132.08" width="0.1524" layer="91"/>
<wire x1="101.6" y1="132.08" x2="101.6" y2="143.51" width="0.1524" layer="91"/>
<wire x1="101.6" y1="143.51" x2="68.58" y2="143.51" width="0.1524" layer="91"/>
<pinref part="C2" gate="G$1" pin="C+"/>
<wire x1="68.58" y1="140.97" x2="68.58" y2="143.51" width="0.1524" layer="91"/>
<pinref part="R1" gate="G$1" pin="P$2"/>
<wire x1="99.06" y1="132.08" x2="101.6" y2="132.08" width="0.1524" layer="91"/>
<junction x="101.6" y="132.08"/>
<pinref part="F1" gate="G$1" pin="OUT"/>
<wire x1="64.77" y1="143.51" x2="68.58" y2="143.51" width="0.1524" layer="91"/>
<junction x="68.58" y="143.51"/>
</segment>
</net>
<net name="N$2" class="0">
<segment>
<pinref part="R1" gate="G$1" pin="P$1"/>
<wire x1="92.71" y1="132.08" x2="86.36" y2="132.08" width="0.1524" layer="91"/>
<pinref part="D1" gate="G$1" pin="A"/>
</segment>
</net>
<net name="VIN_+12V" class="0">
<segment>
<pinref part="J1" gate="G$1" pin="1"/>
<wire x1="40.64" y1="156.21" x2="40.64" y2="157.48" width="0.1524" layer="91"/>
<pinref part="J1" gate="G$1" pin="2"/>
<wire x1="35.56" y1="157.48" x2="35.56" y2="156.21" width="0.1524" layer="91"/>
<wire x1="35.56" y1="156.21" x2="40.64" y2="156.21" width="0.1524" layer="91"/>
<label x="43.18" y="156.21" size="1.27" layer="95"/>
<pinref part="F1" gate="G$1" pin="IN"/>
<wire x1="44.45" y1="143.51" x2="40.64" y2="143.51" width="0.1524" layer="91"/>
<wire x1="40.64" y1="143.51" x2="40.64" y2="156.21" width="0.1524" layer="91"/>
<junction x="40.64" y="156.21"/>
</segment>
</net>
</nets>
</sheet>
</sheets>
</schematic>
</drawing>
<compatibility>
<note version="6.3" minversion="6.2.2" severity="warning">
Since Version 6.2.2 text objects can contain more than one line,
which will not be processed correctly with this version.
</note>
<note version="8.2" severity="warning">
Since Version 8.2, EAGLE supports online libraries. The ids
of those online libraries will not be understood (or retained)
with this version.
</note>
<note version="8.3" severity="warning">
Since Version 8.3, EAGLE supports URNs for individual library
assets (packages, symbols, and devices). The URNs of those assets
will not be understood (or retained) with this version.
</note>
</compatibility>
</eagle>
