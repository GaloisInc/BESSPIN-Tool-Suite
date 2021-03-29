<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE eagle SYSTEM "eagle.dtd">
<eagle version="9.4.0">
<drawing>
<settings>
<setting alwaysvectorfont="no"/>
<setting verticaltext="up"/>
</settings>
<grid distance="0.05" unitdist="inch" unit="inch" style="lines" multiple="1" display="yes" altdistance="0.01" altunitdist="inch" altunit="inch"/>
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
</layers>
<schematic xreflabel="%F%N/%S.%C%R" xrefpart="/%S.%C%R">
<libraries>
<library name="USER_CRYSTALS">
<packages>
<package name="EPSON_FA-238">
<smd name="2" x="1.1" y="-0.8" dx="1.4" dy="1.2" layer="1"/>
<smd name="3" x="1.1" y="0.8" dx="1.4" dy="1.2" layer="1"/>
<smd name="4" x="-1.1" y="0.8" dx="1.4" dy="1.2" layer="1"/>
<smd name="1" x="-1.1" y="-0.8" dx="1.4" dy="1.2" layer="1"/>
<wire x1="-2" y1="1.6" x2="2" y2="1.6" width="0.1524" layer="21"/>
<wire x1="2" y1="1.6" x2="2" y2="-1.6" width="0.1524" layer="21"/>
<wire x1="2" y1="-1.6" x2="-2" y2="-1.6" width="0.1524" layer="21"/>
<wire x1="-2" y1="-1.6" x2="-2" y2="1.6" width="0.1524" layer="21"/>
<polygon width="0.1524" layer="21">
<vertex x="-2.3" y="-0.8"/>
<vertex x="-2.9" y="-0.4"/>
<vertex x="-2.9" y="-1.2"/>
</polygon>
<text x="-2" y="2" size="1" layer="25" font="vector">&gt;NAME</text>
</package>
</packages>
<symbols>
<symbol name="CRYSTAL">
<pin name="1" x="-3.81" y="0" visible="off" length="short"/>
<pin name="3" x="3.81" y="0" visible="off" length="short" rot="R180"/>
<wire x1="-1.27" y1="2.54" x2="-1.27" y2="-2.54" width="0.1524" layer="94"/>
<wire x1="1.27" y1="2.54" x2="1.27" y2="-2.54" width="0.1524" layer="94"/>
<wire x1="-0.635" y1="-2.54" x2="0.635" y2="-2.54" width="0.1524" layer="94"/>
<wire x1="-0.635" y1="-2.54" x2="-0.635" y2="2.54" width="0.1524" layer="94"/>
<wire x1="-0.635" y1="2.54" x2="0.635" y2="2.54" width="0.1524" layer="94"/>
<wire x1="0.635" y1="2.54" x2="0.635" y2="-2.54" width="0.1524" layer="94"/>
<wire x1="-1.905" y1="3.175" x2="1.905" y2="3.175" width="0.1524" layer="94" style="shortdash"/>
<wire x1="1.905" y1="3.175" x2="1.905" y2="-3.175" width="0.1524" layer="94" style="shortdash"/>
<wire x1="1.905" y1="-3.175" x2="-1.905" y2="-3.175" width="0.1524" layer="94" style="shortdash"/>
<wire x1="-1.905" y1="-3.175" x2="-1.905" y2="3.175" width="0.1524" layer="94" style="shortdash"/>
<pin name="GND@2" x="-2.54" y="-6.35" visible="off" length="short" rot="R90"/>
<pin name="GND@4" x="2.54" y="-6.35" visible="off" length="short" rot="R90"/>
<text x="0" y="7.62" size="1.27" layer="95" font="vector" align="bottom-center">&gt;NAME</text>
<text x="0" y="5.08" size="1.27" layer="96" font="vector" align="bottom-center">&gt;VALUE</text>
<wire x1="-2.54" y1="-3.81" x2="-1.905" y2="-3.175" width="0.254" layer="94"/>
<wire x1="2.54" y1="-3.81" x2="1.905" y2="-3.175" width="0.254" layer="94"/>
</symbol>
</symbols>
<devicesets>
<deviceset name="CRYSTAL" prefix="Y" uservalue="yes">
<gates>
<gate name="G$1" symbol="CRYSTAL" x="0" y="0"/>
</gates>
<devices>
<device name="FA-238" package="EPSON_FA-238">
<connects>
<connect gate="G$1" pin="1" pad="1"/>
<connect gate="G$1" pin="3" pad="3"/>
<connect gate="G$1" pin="GND@2" pad="2"/>
<connect gate="G$1" pin="GND@4" pad="4"/>
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
<symbol name="C">
<pin name="P$1" x="-2.54" y="0" visible="off" length="short" direction="pas"/>
<pin name="P$2" x="3.81" y="0" visible="off" length="short" direction="pas" rot="R180"/>
<wire x1="0" y1="1.27" x2="0" y2="-1.27" width="0.254" layer="94"/>
<wire x1="1.27" y1="1.27" x2="1.27" y2="-1.27" width="0.254" layer="94"/>
<text x="-1.27" y="2.54" size="1.27" layer="95" font="vector">&gt;NAME</text>
<text x="-1.27" y="-3.81" size="1.27" layer="96" font="vector">&gt;VALUE</text>
<text x="-1.27" y="-6.35" size="1.27" layer="97" font="vector">&gt;PACKAGE</text>
</symbol>
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
<library name="USER_CON_PINS">
<packages>
<package name="2X3_100MIL_ICSP">
<pad name="1" x="-1.27" y="2.54" drill="1.016" diameter="1.778" shape="square"/>
<pad name="2" x="1.27" y="2.54" drill="1.016" diameter="1.778"/>
<pad name="3" x="-1.27" y="0" drill="1.016" diameter="1.778"/>
<pad name="4" x="1.27" y="0" drill="1.016" diameter="1.778"/>
<pad name="5" x="-1.27" y="-2.54" drill="1.016" diameter="1.778"/>
<pad name="6" x="1.27" y="-2.54" drill="1.016" diameter="1.778"/>
<wire x1="-2.54" y1="3.81" x2="2.54" y2="3.81" width="0.1524" layer="21"/>
<wire x1="2.54" y1="3.81" x2="2.54" y2="-3.81" width="0.1524" layer="21"/>
<wire x1="2.54" y1="-3.81" x2="-2.54" y2="-3.81" width="0.1524" layer="21"/>
<wire x1="-2.54" y1="-3.81" x2="-2.54" y2="3.81" width="0.1524" layer="21"/>
<text x="0" y="5.08" size="1.27" layer="21" font="vector" align="bottom-center">ICSP</text>
<text x="0" y="-6.35" size="1.27" layer="25" font="vector" align="bottom-center">&gt;NAME</text>
</package>
<package name="1X6_100MIL_SMT">
<wire x1="7.747" y1="1.27" x2="7.747" y2="-1.27" width="0.127" layer="21"/>
<wire x1="-7.747" y1="1.27" x2="-7.747" y2="-1.27" width="0.127" layer="21"/>
<wire x1="-7.747" y1="-1.27" x2="7.747" y2="-1.27" width="0.127" layer="21"/>
<wire x1="-7.747" y1="1.27" x2="7.747" y2="1.27" width="0.127" layer="21"/>
<smd name="3" x="1.27" y="-1.651" dx="2.0066" dy="0.9906" layer="1" rot="R90"/>
<smd name="2" x="3.81" y="1.651" dx="2.0066" dy="0.9906" layer="1" rot="R90"/>
<smd name="1" x="6.35" y="-1.651" dx="2.0066" dy="0.9906" layer="1" rot="R90"/>
<smd name="4" x="-1.27" y="1.651" dx="2.0066" dy="0.9906" layer="1" rot="R90"/>
<smd name="5" x="-3.81" y="-1.651" dx="2.0066" dy="0.9906" layer="1" rot="R90"/>
<polygon width="0.127" layer="21">
<vertex x="6.35" y="-2.921"/>
<vertex x="5.842" y="-3.937"/>
<vertex x="6.858" y="-3.937"/>
</polygon>
<text x="-8.128" y="-1.27" size="1.016" layer="25" font="vector" rot="R90">&gt;NAME</text>
<smd name="6" x="-6.35" y="1.651" dx="2.0066" dy="0.9906" layer="1" rot="R90"/>
</package>
<package name="1X6_100MIL_THRU">
<pad name="1" x="0" y="6.35" drill="1.016" shape="square"/>
<pad name="2" x="0" y="3.81" drill="1.016"/>
<pad name="3" x="0" y="1.27" drill="1.016"/>
<pad name="4" x="0" y="-1.27" drill="1.016"/>
<pad name="5" x="0" y="-3.81" drill="1.016"/>
<pad name="6" x="0" y="-6.35" drill="1.016"/>
<wire x1="-0.635" y1="-7.62" x2="0.635" y2="-7.62" width="0.127" layer="21"/>
<wire x1="0.635" y1="-7.62" x2="1.27" y2="-6.985" width="0.127" layer="21"/>
<wire x1="1.27" y1="-6.985" x2="1.27" y2="7.62" width="0.127" layer="21"/>
<wire x1="1.27" y1="7.62" x2="-1.27" y2="7.62" width="0.127" layer="21"/>
<wire x1="-1.27" y1="7.62" x2="-1.27" y2="-6.985" width="0.127" layer="21"/>
<wire x1="-1.27" y1="-6.985" x2="-0.635" y2="-7.62" width="0.127" layer="21"/>
<text x="-3.175" y="7.62" size="1.016" layer="25" font="vector" rot="R270">&gt;NAME</text>
</package>
<package name="1X11_100MIL_THRU">
<pad name="1" x="0" y="12.7" drill="1.016" shape="square"/>
<pad name="2" x="0" y="10.16" drill="1.016"/>
<pad name="3" x="0" y="7.62" drill="1.016"/>
<pad name="4" x="0" y="5.08" drill="1.016"/>
<pad name="5" x="0" y="2.54" drill="1.016"/>
<pad name="6" x="0" y="0" drill="1.016"/>
<wire x1="-0.635" y1="-13.97" x2="0.635" y2="-13.97" width="0.127" layer="21"/>
<wire x1="0.635" y1="-13.97" x2="1.27" y2="-13.335" width="0.127" layer="21"/>
<wire x1="1.27" y1="-13.335" x2="1.27" y2="13.97" width="0.127" layer="21"/>
<wire x1="1.27" y1="13.97" x2="-1.27" y2="13.97" width="0.127" layer="21"/>
<wire x1="-1.27" y1="13.97" x2="-1.27" y2="-13.335" width="0.127" layer="21"/>
<wire x1="-1.27" y1="-13.335" x2="-0.635" y2="-13.97" width="0.127" layer="21"/>
<text x="-3.175" y="13.97" size="1.016" layer="25" font="vector" rot="R270">&gt;NAME</text>
<pad name="7" x="0" y="-2.54" drill="1.016"/>
<pad name="8" x="0" y="-5.08" drill="1.016"/>
<pad name="9" x="0" y="-7.62" drill="1.016"/>
<pad name="10" x="0" y="-10.16" drill="1.016"/>
<pad name="11" x="0" y="-12.7" drill="1.016"/>
</package>
<package name="1X2_100MIL_THRU">
<pad name="1" x="0" y="1.27" drill="1.1" shape="square"/>
<pad name="2" x="0" y="-1.27" drill="1.1"/>
<wire x1="-1.27" y1="2.54" x2="1.27" y2="2.54" width="0.127" layer="21"/>
<wire x1="1.27" y1="2.54" x2="1.27" y2="-2.54" width="0.127" layer="21"/>
<wire x1="1.27" y1="-2.54" x2="-1.27" y2="-2.54" width="0.127" layer="21"/>
<wire x1="-1.27" y1="-2.54" x2="-1.27" y2="2.54" width="0.127" layer="21"/>
<text x="-2.54" y="0" size="1.016" layer="25" font="vector" rot="R90" align="bottom-center">&gt;NAME</text>
</package>
<package name="1X2_3MM_SMT">
<smd name="1" x="0" y="1.5" dx="1.5" dy="3" layer="1" rot="R90"/>
<smd name="2" x="0" y="-1.5" dx="1.5" dy="3" layer="1" rot="R90"/>
<wire x1="-1.75" y1="2.5" x2="1.75" y2="2.5" width="0.127" layer="21"/>
<wire x1="1.75" y1="2.5" x2="1.75" y2="-2.5" width="0.127" layer="21"/>
<wire x1="1.75" y1="-2.5" x2="-1.75" y2="-2.5" width="0.127" layer="21"/>
<wire x1="-1.75" y1="-2.5" x2="-1.75" y2="2.5" width="0.127" layer="21"/>
</package>
</packages>
<symbols>
<symbol name="2X3_ICSP">
<pin name="MISO" x="-15.24" y="5.08" length="middle"/>
<pin name="SCK" x="-15.24" y="0" length="middle"/>
<pin name="RST" x="-15.24" y="-5.08" length="middle"/>
<pin name="GND" x="15.24" y="-5.08" length="middle" rot="R180"/>
<pin name="MOSI" x="15.24" y="0" length="middle" rot="R180"/>
<pin name="VCC" x="15.24" y="5.08" length="middle" rot="R180"/>
<wire x1="-10.16" y1="7.62" x2="-10.16" y2="-7.62" width="0.1524" layer="94"/>
<wire x1="-10.16" y1="-7.62" x2="10.16" y2="-7.62" width="0.1524" layer="94"/>
<wire x1="10.16" y1="-7.62" x2="10.16" y2="7.62" width="0.1524" layer="94"/>
<wire x1="10.16" y1="7.62" x2="-10.16" y2="7.62" width="0.1524" layer="94"/>
<text x="-10.16" y="-12.7" size="1.27" layer="96" font="vector">&gt;VALUE</text>
<text x="-10.16" y="-10.16" size="1.27" layer="95" font="vector">&gt;NAME</text>
<text x="0" y="8.89" size="1.27" layer="94" font="vector" align="bottom-center">ICSP</text>
</symbol>
<symbol name="1X6">
<pin name="1" x="-5.08" y="12.7" visible="pin" length="short"/>
<pin name="2" x="-5.08" y="7.62" visible="pin" length="short"/>
<pin name="3" x="-5.08" y="2.54" visible="pin" length="short"/>
<pin name="4" x="-5.08" y="-2.54" visible="pin" length="short"/>
<pin name="5" x="-5.08" y="-7.62" visible="pin" length="short"/>
<wire x1="-2.54" y1="15.24" x2="-2.54" y2="-15.24" width="0.254" layer="94"/>
<wire x1="-2.54" y1="-15.24" x2="2.54" y2="-15.24" width="0.254" layer="94"/>
<wire x1="2.54" y1="-15.24" x2="2.54" y2="15.24" width="0.254" layer="94"/>
<wire x1="2.54" y1="15.24" x2="-2.54" y2="15.24" width="0.254" layer="94"/>
<text x="-2.54" y="16.51" size="1.27" layer="95" font="vector">&gt;NAME</text>
<text x="-2.54" y="-17.78" size="1.27" layer="96" font="vector">&gt;VALUE</text>
<pin name="6" x="-5.08" y="-12.7" visible="pin" length="short"/>
</symbol>
<symbol name="1X11">
<pin name="1" x="-5.08" y="25.4" visible="pin" length="short"/>
<pin name="2" x="-5.08" y="20.32" visible="pin" length="short"/>
<pin name="3" x="-5.08" y="15.24" visible="pin" length="short"/>
<pin name="4" x="-5.08" y="10.16" visible="pin" length="short"/>
<pin name="5" x="-5.08" y="5.08" visible="pin" length="short"/>
<wire x1="-2.54" y1="27.94" x2="-2.54" y2="-27.94" width="0.254" layer="94"/>
<wire x1="-2.54" y1="-27.94" x2="5.08" y2="-27.94" width="0.254" layer="94"/>
<wire x1="5.08" y1="-27.94" x2="5.08" y2="27.94" width="0.254" layer="94"/>
<wire x1="5.08" y1="27.94" x2="-2.54" y2="27.94" width="0.254" layer="94"/>
<text x="-2.54" y="29.21" size="1.27" layer="95" font="vector">&gt;NAME</text>
<text x="-2.54" y="-30.48" size="1.27" layer="96" font="vector">&gt;VALUE</text>
<pin name="6" x="-5.08" y="0" visible="pin" length="short"/>
<pin name="7" x="-5.08" y="-5.08" visible="pin" length="short"/>
<pin name="8" x="-5.08" y="-10.16" visible="pin" length="short"/>
<pin name="9" x="-5.08" y="-15.24" visible="pin" length="short"/>
<pin name="10" x="-5.08" y="-20.32" visible="pin" length="short"/>
<pin name="11" x="-5.08" y="-25.4" visible="pin" length="short"/>
</symbol>
<symbol name="1X2">
<pin name="1" x="-5.08" y="2.54" visible="pin" length="middle"/>
<pin name="2" x="-5.08" y="-2.54" visible="pin" length="middle"/>
<wire x1="0" y1="5.08" x2="0" y2="-5.08" width="0.254" layer="94"/>
<wire x1="0" y1="-5.08" x2="5.08" y2="-5.08" width="0.254" layer="94"/>
<wire x1="5.08" y1="-5.08" x2="5.08" y2="5.08" width="0.254" layer="94"/>
<wire x1="5.08" y1="5.08" x2="0" y2="5.08" width="0.254" layer="94"/>
<text x="0" y="6.35" size="1.27" layer="95" font="vector">&gt;NAME</text>
<text x="0" y="-7.62" size="1.27" layer="96" font="vector">&gt;VALUE</text>
</symbol>
</symbols>
<devicesets>
<deviceset name="2X3_ICSP" prefix="CN" uservalue="yes">
<gates>
<gate name="G$1" symbol="2X3_ICSP" x="0" y="0"/>
</gates>
<devices>
<device name="ARDUINO_ICSP" package="2X3_100MIL_ICSP">
<connects>
<connect gate="G$1" pin="GND" pad="6"/>
<connect gate="G$1" pin="MISO" pad="1"/>
<connect gate="G$1" pin="MOSI" pad="4"/>
<connect gate="G$1" pin="RST" pad="5"/>
<connect gate="G$1" pin="SCK" pad="3"/>
<connect gate="G$1" pin="VCC" pad="2"/>
</connects>
<technologies>
<technology name="">
<attribute name="MPN" value="" constant="no"/>
</technology>
</technologies>
</device>
</devices>
</deviceset>
<deviceset name="1X6" prefix="CN" uservalue="yes">
<gates>
<gate name="G$1" symbol="1X6" x="0" y="0"/>
</gates>
<devices>
<device name="SMT" package="1X6_100MIL_SMT">
<connects>
<connect gate="G$1" pin="1" pad="1"/>
<connect gate="G$1" pin="2" pad="2"/>
<connect gate="G$1" pin="3" pad="3"/>
<connect gate="G$1" pin="4" pad="4"/>
<connect gate="G$1" pin="5" pad="5"/>
<connect gate="G$1" pin="6" pad="6"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
<device name="THRU" package="1X6_100MIL_THRU">
<connects>
<connect gate="G$1" pin="1" pad="1"/>
<connect gate="G$1" pin="2" pad="2"/>
<connect gate="G$1" pin="3" pad="3"/>
<connect gate="G$1" pin="4" pad="4"/>
<connect gate="G$1" pin="5" pad="5"/>
<connect gate="G$1" pin="6" pad="6"/>
</connects>
<technologies>
<technology name="">
<attribute name="MPN" value="" constant="no"/>
</technology>
</technologies>
</device>
</devices>
</deviceset>
<deviceset name="1X11" prefix="CN" uservalue="yes">
<gates>
<gate name="G$1" symbol="1X11" x="0" y="0"/>
</gates>
<devices>
<device name="" package="1X11_100MIL_THRU">
<connects>
<connect gate="G$1" pin="1" pad="1"/>
<connect gate="G$1" pin="10" pad="10"/>
<connect gate="G$1" pin="11" pad="11"/>
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
</devices>
</deviceset>
<deviceset name="1X2" prefix="J" uservalue="yes">
<gates>
<gate name="G$1" symbol="1X2" x="0" y="0"/>
</gates>
<devices>
<device name="" package="1X2_100MIL_THRU">
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
<device name="SMT_3MM_PITCH" package="1X2_3MM_SMT">
<connects>
<connect gate="G$1" pin="1" pad="1"/>
<connect gate="G$1" pin="2" pad="2"/>
</connects>
<technologies>
<technology name=""/>
</technologies>
</device>
</devices>
</deviceset>
</devicesets>
</library>
<library name="USER_DIODES">
<packages>
<package name="SOD-123">
<smd name="A" x="-1.6383" y="0" dx="1.2192" dy="0.9144" layer="1" rot="R90"/>
<smd name="C" x="1.6383" y="0" dx="1.2192" dy="0.9144" layer="1" rot="R90"/>
<wire x1="-1.016" y1="0.762" x2="1.016" y2="0.762" width="0.127" layer="21"/>
<wire x1="1.016" y1="0.762" x2="1.016" y2="-0.762" width="0.127" layer="21"/>
<wire x1="1.016" y1="-0.762" x2="-1.016" y2="-0.762" width="0.127" layer="21"/>
<wire x1="-1.016" y1="-0.762" x2="-1.016" y2="0.762" width="0.127" layer="21"/>
<rectangle x1="0.381" y1="-0.762" x2="1.016" y2="0.762" layer="21"/>
<rectangle x1="2.286" y1="-0.762" x2="2.54" y2="0.762" layer="21"/>
<rectangle x1="-2.413" y1="-1.016" x2="2.794" y2="1.016" layer="39"/>
<text x="0" y="1.143" size="1.016" layer="25" font="vector" align="bottom-center">&gt;NAME</text>
</package>
</packages>
<symbols>
<symbol name="SILICON">
<pin name="A" x="-3.81" y="0" visible="off" length="short"/>
<pin name="C" x="3.81" y="0" visible="off" length="short" rot="R180"/>
<wire x1="-1.27" y1="1.27" x2="-1.27" y2="-1.27" width="0.254" layer="94"/>
<wire x1="-1.27" y1="-1.27" x2="1.27" y2="0" width="0.254" layer="94"/>
<wire x1="1.27" y1="0" x2="-1.27" y2="1.27" width="0.254" layer="94"/>
<wire x1="1.27" y1="1.27" x2="1.27" y2="-1.27" width="0.254" layer="94"/>
<text x="-1.27" y="2.54" size="1.27" layer="95" font="vector">&gt;NAME</text>
<text x="-1.27" y="-3.81" size="1.27" layer="96" font="vector">&gt;VALUE</text>
</symbol>
</symbols>
<devicesets>
<deviceset name="SILICON" prefix="D" uservalue="yes">
<gates>
<gate name="G$1" symbol="SILICON" x="0" y="0"/>
</gates>
<devices>
<device name="" package="SOD-123">
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
<library name="USER_AVR_MICROCONTROLLERS">
<packages>
<package name="TQFP-44">
<wire x1="4.5" y1="-5" x2="5" y2="-4.5" width="0.127" layer="21"/>
<wire x1="5" y1="-4.5" x2="5" y2="4.5" width="0.127" layer="21"/>
<wire x1="5" y1="4.5" x2="4.5" y2="5" width="0.127" layer="21"/>
<wire x1="4.5" y1="5" x2="-4.5" y2="5" width="0.127" layer="21"/>
<wire x1="-4.5" y1="5" x2="-5" y2="4.5" width="0.127" layer="21"/>
<wire x1="-5" y1="4.5" x2="-5" y2="-4.5" width="0.127" layer="21"/>
<wire x1="-5" y1="-4.5" x2="-4.5" y2="-5" width="0.127" layer="21"/>
<wire x1="-4.5" y1="-5" x2="4.5" y2="-5" width="0.127" layer="21"/>
<rectangle x1="-0.2" y1="5" x2="0.2" y2="6" layer="51"/>
<rectangle x1="-5.7" y1="-0.5" x2="-5.3" y2="0.5" layer="51" rot="R90"/>
<rectangle x1="-0.2" y1="-6" x2="0.2" y2="-5" layer="51"/>
<rectangle x1="5.3" y1="-0.5" x2="5.7" y2="0.5" layer="51" rot="R90"/>
<rectangle x1="-5.7" y1="0.3" x2="-5.3" y2="1.3" layer="51" rot="R90"/>
<rectangle x1="-5.7" y1="1.1" x2="-5.3" y2="2.1" layer="51" rot="R90"/>
<rectangle x1="-5.7" y1="1.9" x2="-5.3" y2="2.9" layer="51" rot="R90"/>
<rectangle x1="-5.7" y1="2.7" x2="-5.3" y2="3.7" layer="51" rot="R90"/>
<rectangle x1="-5.7" y1="-1.3" x2="-5.3" y2="-0.3" layer="51" rot="R90"/>
<rectangle x1="-5.7" y1="-2.1" x2="-5.3" y2="-1.1" layer="51" rot="R90"/>
<rectangle x1="-5.7" y1="-2.9" x2="-5.3" y2="-1.9" layer="51" rot="R90"/>
<rectangle x1="-5.7" y1="-3.7" x2="-5.3" y2="-2.7" layer="51" rot="R90"/>
<rectangle x1="-5.7" y1="3.5" x2="-5.3" y2="4.5" layer="51" rot="R90"/>
<rectangle x1="-5.7" y1="-4.5" x2="-5.3" y2="-3.5" layer="51" rot="R90"/>
<rectangle x1="-1" y1="-6" x2="-0.6" y2="-5" layer="51"/>
<rectangle x1="-1.8" y1="-6" x2="-1.4" y2="-5" layer="51"/>
<rectangle x1="-2.6" y1="-6" x2="-2.2" y2="-5" layer="51"/>
<rectangle x1="-3.4" y1="-6" x2="-3" y2="-5" layer="51"/>
<rectangle x1="-4.2" y1="-6" x2="-3.8" y2="-5" layer="51"/>
<rectangle x1="0.6" y1="-6" x2="1" y2="-5" layer="51"/>
<rectangle x1="1.4" y1="-6" x2="1.8" y2="-5" layer="51"/>
<rectangle x1="2.2" y1="-6" x2="2.6" y2="-5" layer="51"/>
<rectangle x1="3" y1="-6" x2="3.4" y2="-5" layer="51"/>
<rectangle x1="3.8" y1="-6" x2="4.2" y2="-5" layer="51"/>
<rectangle x1="5.3" y1="-1.3" x2="5.7" y2="-0.3" layer="51" rot="R90"/>
<rectangle x1="5.3" y1="-2.1" x2="5.7" y2="-1.1" layer="51" rot="R90"/>
<rectangle x1="5.3" y1="-2.9" x2="5.7" y2="-1.9" layer="51" rot="R90"/>
<rectangle x1="5.3" y1="-3.7" x2="5.7" y2="-2.7" layer="51" rot="R90"/>
<rectangle x1="5.3" y1="-4.5" x2="5.7" y2="-3.5" layer="51" rot="R90"/>
<rectangle x1="5.3" y1="0.3" x2="5.7" y2="1.3" layer="51" rot="R90"/>
<rectangle x1="5.3" y1="1.1" x2="5.7" y2="2.1" layer="51" rot="R90"/>
<rectangle x1="5.3" y1="1.9" x2="5.7" y2="2.9" layer="51" rot="R90"/>
<rectangle x1="5.3" y1="2.7" x2="5.7" y2="3.7" layer="51" rot="R90"/>
<rectangle x1="5.3" y1="3.5" x2="5.7" y2="4.5" layer="51" rot="R90"/>
<rectangle x1="0.6" y1="5" x2="1" y2="6" layer="51"/>
<rectangle x1="1.4" y1="5" x2="1.8" y2="6" layer="51"/>
<rectangle x1="2.2" y1="5" x2="2.6" y2="6" layer="51"/>
<rectangle x1="3" y1="5" x2="3.4" y2="6" layer="51"/>
<rectangle x1="3.8" y1="5" x2="4.2" y2="6" layer="51"/>
<rectangle x1="-1" y1="5" x2="-0.6" y2="6" layer="51"/>
<rectangle x1="-1.8" y1="5" x2="-1.4" y2="6" layer="51"/>
<rectangle x1="-2.6" y1="5" x2="-2.2" y2="6" layer="51"/>
<rectangle x1="-3.4" y1="5" x2="-3" y2="6" layer="51"/>
<rectangle x1="-4.2" y1="5" x2="-3.8" y2="6" layer="51"/>
<polygon width="0.127" layer="21">
<vertex x="-6.7" y="4"/>
<vertex x="-7.2" y="4.3"/>
<vertex x="-7.2" y="3.7"/>
</polygon>
<smd name="1" x="-5.6" y="4" dx="1.6" dy="0.55" layer="1"/>
<smd name="2" x="-5.6" y="3.2" dx="1.6" dy="0.55" layer="1"/>
<smd name="3" x="-5.6" y="2.4" dx="1.6" dy="0.55" layer="1"/>
<smd name="4" x="-5.6" y="1.6" dx="1.6" dy="0.55" layer="1"/>
<smd name="5" x="-5.6" y="0.8" dx="1.6" dy="0.55" layer="1"/>
<smd name="6" x="-5.6" y="0" dx="1.6" dy="0.55" layer="1"/>
<smd name="7" x="-5.6" y="-0.8" dx="1.6" dy="0.55" layer="1"/>
<smd name="8" x="-5.6" y="-1.6" dx="1.6" dy="0.55" layer="1"/>
<smd name="9" x="-5.6" y="-2.4" dx="1.6" dy="0.55" layer="1"/>
<smd name="10" x="-5.6" y="-3.2" dx="1.6" dy="0.55" layer="1"/>
<smd name="11" x="-5.6" y="-4" dx="1.6" dy="0.55" layer="1"/>
<smd name="12" x="-4" y="-5.6" dx="1.6" dy="0.55" layer="1" rot="R270"/>
<smd name="13" x="-3.2" y="-5.6" dx="1.6" dy="0.55" layer="1" rot="R270"/>
<smd name="14" x="-2.4" y="-5.6" dx="1.6" dy="0.55" layer="1" rot="R270"/>
<smd name="15" x="-1.6" y="-5.6" dx="1.6" dy="0.55" layer="1" rot="R270"/>
<smd name="16" x="-0.8" y="-5.6" dx="1.6" dy="0.55" layer="1" rot="R270"/>
<smd name="17" x="0" y="-5.6" dx="1.6" dy="0.55" layer="1" rot="R270"/>
<smd name="18" x="0.8" y="-5.6" dx="1.6" dy="0.55" layer="1" rot="R270"/>
<smd name="19" x="1.6" y="-5.6" dx="1.6" dy="0.55" layer="1" rot="R270"/>
<smd name="20" x="2.4" y="-5.6" dx="1.6" dy="0.55" layer="1" rot="R270"/>
<smd name="21" x="3.2" y="-5.6" dx="1.6" dy="0.55" layer="1" rot="R270"/>
<smd name="22" x="4" y="-5.6" dx="1.6" dy="0.55" layer="1" rot="R270"/>
<smd name="23" x="5.6" y="-4" dx="1.6" dy="0.55" layer="1"/>
<smd name="24" x="5.6" y="-3.2" dx="1.6" dy="0.55" layer="1"/>
<smd name="25" x="5.6" y="-2.4" dx="1.6" dy="0.55" layer="1"/>
<smd name="26" x="5.6" y="-1.6" dx="1.6" dy="0.55" layer="1"/>
<smd name="27" x="5.6" y="-0.8" dx="1.6" dy="0.55" layer="1"/>
<smd name="28" x="5.6" y="0" dx="1.6" dy="0.55" layer="1"/>
<smd name="29" x="5.6" y="0.8" dx="1.6" dy="0.55" layer="1"/>
<smd name="30" x="5.6" y="1.6" dx="1.6" dy="0.55" layer="1"/>
<smd name="31" x="5.6" y="2.4" dx="1.6" dy="0.55" layer="1"/>
<smd name="32" x="5.6" y="3.2" dx="1.6" dy="0.55" layer="1"/>
<smd name="33" x="5.6" y="4" dx="1.6" dy="0.55" layer="1"/>
<smd name="34" x="4" y="5.6" dx="1.6" dy="0.55" layer="1" rot="R90"/>
<smd name="35" x="3.2" y="5.6" dx="1.6" dy="0.55" layer="1" rot="R90"/>
<smd name="36" x="2.4" y="5.6" dx="1.6" dy="0.55" layer="1" rot="R90"/>
<smd name="37" x="1.6" y="5.6" dx="1.6" dy="0.55" layer="1" rot="R90"/>
<smd name="38" x="0.8" y="5.6" dx="1.6" dy="0.55" layer="1" rot="R90"/>
<smd name="39" x="0" y="5.6" dx="1.6" dy="0.55" layer="1" rot="R90"/>
<smd name="40" x="-0.8" y="5.6" dx="1.6" dy="0.55" layer="1" rot="R90"/>
<smd name="41" x="-1.6" y="5.6" dx="1.6" dy="0.55" layer="1" rot="R90"/>
<smd name="42" x="-2.4" y="5.6" dx="1.6" dy="0.55" layer="1" rot="R90"/>
<smd name="43" x="-3.2" y="5.6" dx="1.6" dy="0.55" layer="1" rot="R90"/>
<smd name="44" x="-4" y="5.6" dx="1.6" dy="0.55" layer="1" rot="R90"/>
<text x="-7.1" y="4.9" size="1" layer="25" font="vector" align="bottom-center">&gt;NAME</text>
</package>
</packages>
<symbols>
<symbol name="ATMEGA32U4">
<pin name="USB_CAP" x="-27.94" y="22.86" length="middle"/>
<pin name="USB_GND" x="-27.94" y="-30.48" length="middle"/>
<pin name="D+" x="-27.94" y="10.16" length="middle"/>
<pin name="D-" x="-27.94" y="15.24" length="middle"/>
<pin name="USB_VCC" x="-27.94" y="40.64" length="middle"/>
<pin name="PE6/INT6/AIN0" x="30.48" y="-15.24" length="middle" rot="R180"/>
<pin name="VBUS" x="-27.94" y="38.1" length="middle"/>
<pin name="PB0/SS/PCINT0" x="30.48" y="20.32" length="middle" rot="R180"/>
<pin name="PB1/PCINT1/SCL" x="30.48" y="22.86" length="middle" rot="R180"/>
<pin name="PB2/PDI/PCINT2/MOSI" x="30.48" y="25.4" length="middle" rot="R180"/>
<pin name="PB3/PDO/PCINT3/MISO" x="30.48" y="27.94" length="middle" rot="R180"/>
<pin name="XTAL1" x="-27.94" y="-25.4" length="middle"/>
<pin name="XTAL2" x="-27.94" y="-20.32" length="middle"/>
<pin name="GND@15" x="-27.94" y="-33.02" length="middle"/>
<pin name="VCC@14" x="-27.94" y="35.56" length="middle"/>
<pin name="!RESET" x="-27.94" y="-15.24" length="middle"/>
<pin name="PB7/PCINT7/OC0A/OC1C/!RTS" x="30.48" y="38.1" length="middle" rot="R180"/>
<pin name="PD0/OC0B/SCL/INT0" x="30.48" y="-10.16" length="middle" rot="R180"/>
<pin name="PD1/SDA/INT1" x="30.48" y="-7.62" length="middle" rot="R180"/>
<pin name="PD2/RXD1/INT2" x="30.48" y="-5.08" length="middle" rot="R180"/>
<pin name="PD3/TXD1/INT3" x="30.48" y="-2.54" length="middle" rot="R180"/>
<pin name="PD5/XCK1/!CTS" x="30.48" y="2.54" length="middle" rot="R180"/>
<pin name="PB4/PCINT4/ADC11" x="30.48" y="30.48" length="middle" rot="R180"/>
<pin name="PD7/T0/OC4D/ADC10" x="30.48" y="7.62" length="middle" rot="R180"/>
<pin name="PD6/T1/!OC4D!/ADC9" x="30.48" y="5.08" length="middle" rot="R180"/>
<pin name="PD4/ICP1/ADC8" x="30.48" y="0" length="middle" rot="R180"/>
<pin name="AVCC@24" x="-27.94" y="30.48" length="middle"/>
<pin name="GND@23" x="-27.94" y="-35.56" length="middle"/>
<pin name="PB5/PCINT5/OC1A/!OC4B!/ADC12" x="30.48" y="33.02" length="middle" rot="R180"/>
<pin name="PB6/PCINT6/OC1B/OC4B/ADC13" x="30.48" y="35.56" length="middle" rot="R180"/>
<pin name="PC6/OC3A/!OC4A" x="30.48" y="12.7" length="middle" rot="R180"/>
<pin name="PC7/ICP3/CLK0/OC4A" x="30.48" y="15.24" length="middle" rot="R180"/>
<pin name="PE2/!HWB" x="30.48" y="-17.78" length="middle" rot="R180"/>
<pin name="PF4/ADC4/TCK" x="30.48" y="-30.48" length="middle" rot="R180"/>
<pin name="PF5/ADC5/TMS" x="30.48" y="-27.94" length="middle" rot="R180"/>
<pin name="PF6/ADC6/TDO" x="30.48" y="-25.4" length="middle" rot="R180"/>
<pin name="PF7/ADC7/TDI" x="30.48" y="-22.86" length="middle" rot="R180"/>
<pin name="GND@35" x="-27.94" y="-38.1" length="middle"/>
<pin name="VCC@34" x="-27.94" y="33.02" length="middle"/>
<pin name="PF1/ADC1" x="30.48" y="-38.1" length="middle" rot="R180"/>
<pin name="PF0/ADC0" x="30.48" y="-40.64" length="middle" rot="R180"/>
<pin name="AREF" x="-27.94" y="-2.54" length="middle"/>
<pin name="GND@43" x="-27.94" y="-40.64" length="middle"/>
<pin name="AVCC@44" x="-27.94" y="27.94" length="middle"/>
<wire x1="-22.86" y1="43.18" x2="25.4" y2="43.18" width="0.254" layer="94"/>
<wire x1="25.4" y1="43.18" x2="25.4" y2="-43.18" width="0.254" layer="94"/>
<wire x1="25.4" y1="-43.18" x2="-22.86" y2="-43.18" width="0.254" layer="94"/>
<wire x1="-22.86" y1="-43.18" x2="-22.86" y2="43.18" width="0.254" layer="94"/>
<text x="-22.86" y="45.72" size="1.27" layer="95" font="vector">&gt;NAME</text>
<text x="-22.86" y="-45.72" size="1.27" layer="95" font="vector">&gt;VALUE</text>
<text x="-22.86" y="-48.26" size="1.27" layer="97" font="vector">&gt;PACKAGE</text>
</symbol>
</symbols>
<devicesets>
<deviceset name="ATMEGA32U4" prefix="U" uservalue="yes">
<gates>
<gate name="G$1" symbol="ATMEGA32U4" x="0" y="0"/>
</gates>
<devices>
<device name="TQFP-44" package="TQFP-44">
<connects>
<connect gate="G$1" pin="!RESET" pad="13"/>
<connect gate="G$1" pin="AREF" pad="42"/>
<connect gate="G$1" pin="AVCC@24" pad="24"/>
<connect gate="G$1" pin="AVCC@44" pad="44"/>
<connect gate="G$1" pin="D+" pad="4"/>
<connect gate="G$1" pin="D-" pad="3"/>
<connect gate="G$1" pin="GND@15" pad="15"/>
<connect gate="G$1" pin="GND@23" pad="23"/>
<connect gate="G$1" pin="GND@35" pad="35"/>
<connect gate="G$1" pin="GND@43" pad="43"/>
<connect gate="G$1" pin="PB0/SS/PCINT0" pad="8"/>
<connect gate="G$1" pin="PB1/PCINT1/SCL" pad="9"/>
<connect gate="G$1" pin="PB2/PDI/PCINT2/MOSI" pad="10"/>
<connect gate="G$1" pin="PB3/PDO/PCINT3/MISO" pad="11"/>
<connect gate="G$1" pin="PB4/PCINT4/ADC11" pad="28"/>
<connect gate="G$1" pin="PB5/PCINT5/OC1A/!OC4B!/ADC12" pad="29"/>
<connect gate="G$1" pin="PB6/PCINT6/OC1B/OC4B/ADC13" pad="30"/>
<connect gate="G$1" pin="PB7/PCINT7/OC0A/OC1C/!RTS" pad="12"/>
<connect gate="G$1" pin="PC6/OC3A/!OC4A" pad="31"/>
<connect gate="G$1" pin="PC7/ICP3/CLK0/OC4A" pad="32"/>
<connect gate="G$1" pin="PD0/OC0B/SCL/INT0" pad="18"/>
<connect gate="G$1" pin="PD1/SDA/INT1" pad="19"/>
<connect gate="G$1" pin="PD2/RXD1/INT2" pad="20"/>
<connect gate="G$1" pin="PD3/TXD1/INT3" pad="21"/>
<connect gate="G$1" pin="PD4/ICP1/ADC8" pad="25"/>
<connect gate="G$1" pin="PD5/XCK1/!CTS" pad="22"/>
<connect gate="G$1" pin="PD6/T1/!OC4D!/ADC9" pad="26"/>
<connect gate="G$1" pin="PD7/T0/OC4D/ADC10" pad="27"/>
<connect gate="G$1" pin="PE2/!HWB" pad="33"/>
<connect gate="G$1" pin="PE6/INT6/AIN0" pad="1"/>
<connect gate="G$1" pin="PF0/ADC0" pad="41"/>
<connect gate="G$1" pin="PF1/ADC1" pad="40"/>
<connect gate="G$1" pin="PF4/ADC4/TCK" pad="39"/>
<connect gate="G$1" pin="PF5/ADC5/TMS" pad="38"/>
<connect gate="G$1" pin="PF6/ADC6/TDO" pad="37"/>
<connect gate="G$1" pin="PF7/ADC7/TDI" pad="36"/>
<connect gate="G$1" pin="USB_CAP" pad="6"/>
<connect gate="G$1" pin="USB_GND" pad="5"/>
<connect gate="G$1" pin="USB_VCC" pad="2"/>
<connect gate="G$1" pin="VBUS" pad="7"/>
<connect gate="G$1" pin="VCC@14" pad="14"/>
<connect gate="G$1" pin="VCC@34" pad="34"/>
<connect gate="G$1" pin="XTAL1" pad="17"/>
<connect gate="G$1" pin="XTAL2" pad="16"/>
</connects>
<technologies>
<technology name="">
<attribute name="MPN" value="ATMEGA32U4-AUR"/>
<attribute name="PACKAGE" value="TQFP-44"/>
</technology>
</technologies>
</device>
</devices>
</deviceset>
</devicesets>
</library>
<library name="USER_CONN_USB">
<packages>
<package name="AMPHENOL_10118192-0002LF">
<smd name="TAB1" x="-3.1" y="2.55" dx="2.1" dy="1.6" layer="1"/>
<smd name="TAB2" x="3.1" y="2.55" dx="2.1" dy="1.6" layer="1"/>
<smd name="1" x="-1.3" y="2.675" dx="0.4" dy="1.35" layer="1"/>
<smd name="2" x="-0.65" y="2.675" dx="0.4" dy="1.35" layer="1"/>
<smd name="3" x="0" y="2.675" dx="0.4" dy="1.35" layer="1"/>
<smd name="4" x="0.65" y="2.675" dx="0.4" dy="1.35" layer="1"/>
<smd name="5" x="1.3" y="2.675" dx="0.4" dy="1.35" layer="1"/>
<smd name="TAB6" x="-3.8" y="0" dx="1.8" dy="1.9" layer="1"/>
<smd name="TAB3" x="3.8" y="0" dx="1.8" dy="1.9" layer="1"/>
<smd name="TAB5" x="-1.210015625" y="-0.035425" dx="1.9" dy="1.9" layer="1"/>
<smd name="TAB4" x="1.204484375" y="0.029146875" dx="1.9" dy="1.9" layer="1"/>
<wire x1="-4.35" y1="-1.45" x2="4.35" y2="-1.45" width="0" layer="49"/>
<wire x1="-3.75" y1="-2.5" x2="-3.75" y2="2.5" width="0.1" layer="51"/>
<wire x1="3.75" y1="2.5" x2="3.75" y2="-2.5" width="0.1" layer="51"/>
<wire x1="-3.75" y1="-2.5" x2="3.75" y2="-2.5" width="0.1" layer="51"/>
<wire x1="-3.75" y1="2.5" x2="3.75" y2="2.5" width="0.1" layer="51"/>
<text x="0" y="-1.55" size="0.5" layer="51" font="vector" rot="R180" align="bottom-center">PCB EDGE</text>
</package>
</packages>
<symbols>
<symbol name="USB">
<pin name="VBUS" x="-5.08" y="5.08" length="middle"/>
<pin name="D-" x="-5.08" y="2.54" length="middle"/>
<pin name="D+" x="-5.08" y="0" length="middle"/>
<pin name="OTG" x="-5.08" y="-2.54" length="middle"/>
<pin name="GND" x="-5.08" y="-5.08" length="middle"/>
<wire x1="0" y1="7.62" x2="10.16" y2="7.62" width="0.254" layer="94"/>
<wire x1="10.16" y1="7.62" x2="12.7" y2="5.08" width="0.254" layer="94"/>
<wire x1="12.7" y1="5.08" x2="12.7" y2="-5.08" width="0.254" layer="94"/>
<wire x1="12.7" y1="-5.08" x2="10.16" y2="-7.62" width="0.254" layer="94"/>
<wire x1="10.16" y1="-7.62" x2="0" y2="-7.62" width="0.254" layer="94"/>
<wire x1="0" y1="-7.62" x2="0" y2="7.62" width="0.254" layer="94"/>
<text x="0" y="8.89" size="1.27" layer="95">&gt;NAME</text>
<text x="0" y="-10.16" size="1.27" layer="96">&gt;VALUE</text>
<pin name="SHELL" x="-5.08" y="-15.24" length="middle"/>
<wire x1="0" y1="-12.7" x2="0" y2="-17.78" width="0.254" layer="94"/>
<wire x1="0" y1="-17.78" x2="10.16" y2="-17.78" width="0.254" layer="94"/>
<wire x1="10.16" y1="-17.78" x2="10.16" y2="-12.7" width="0.254" layer="94"/>
<wire x1="10.16" y1="-12.7" x2="0" y2="-12.7" width="0.254" layer="94"/>
</symbol>
</symbols>
<devicesets>
<deviceset name="USB_MICRO_B_GENERIC" prefix="CN" uservalue="yes">
<gates>
<gate name="G$1" symbol="USB" x="0" y="0"/>
</gates>
<devices>
<device name="SMT" package="AMPHENOL_10118192-0002LF">
<connects>
<connect gate="G$1" pin="D+" pad="3"/>
<connect gate="G$1" pin="D-" pad="2"/>
<connect gate="G$1" pin="GND" pad="5"/>
<connect gate="G$1" pin="OTG" pad="4"/>
<connect gate="G$1" pin="SHELL" pad="TAB1 TAB2 TAB3 TAB4 TAB5 TAB6"/>
<connect gate="G$1" pin="VBUS" pad="1"/>
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
<package name="SOT23-3">
<smd name="3" x="0" y="1" dx="0.8" dy="0.9" layer="1" rot="R90"/>
<smd name="1" x="-0.95" y="-1" dx="0.8" dy="0.9" layer="1" rot="R90"/>
<smd name="2" x="0.95" y="-1" dx="0.8" dy="0.9" layer="1" rot="R90"/>
<wire x1="1.45" y1="0.65" x2="1.45" y2="-0.65" width="0.127" layer="51"/>
<wire x1="1.45" y1="-0.65" x2="-1.45" y2="-0.65" width="0.127" layer="51"/>
<wire x1="-1.45" y1="-0.65" x2="-1.45" y2="0.65" width="0.127" layer="51"/>
<wire x1="-1.45" y1="0.65" x2="1.45" y2="0.65" width="0.127" layer="51"/>
<text x="-1.651" y="-0.635" size="1.016" layer="25" font="vector" rot="R90">&gt;NAME</text>
<wire x1="-0.55" y1="0.65" x2="-1.45" y2="0.65" width="0.127" layer="21"/>
<wire x1="-1.45" y1="0.65" x2="-1.45" y2="-0.5" width="0.127" layer="21"/>
<wire x1="-0.4" y1="-0.65" x2="0.4" y2="-0.65" width="0.127" layer="21"/>
<wire x1="1.45" y1="-0.5" x2="1.45" y2="0.65" width="0.127" layer="21"/>
<wire x1="1.45" y1="0.65" x2="0.55" y2="0.65" width="0.127" layer="21"/>
<rectangle x1="-0.225" y1="0.7" x2="0.225" y2="1.2" layer="51"/>
<rectangle x1="-1.175" y1="-1.2" x2="-0.725" y2="-0.7" layer="51"/>
<rectangle x1="0.725" y1="-1.2" x2="1.175" y2="-0.7" layer="51"/>
</package>
</packages>
<symbols>
<symbol name="AP2125">
<pin name="VIN" x="-15.24" y="2.54" length="middle"/>
<pin name="VOUT" x="15.24" y="2.54" length="middle" rot="R180"/>
<pin name="GND" x="0" y="-10.16" length="middle" rot="R90"/>
<wire x1="-10.16" y1="5.08" x2="10.16" y2="5.08" width="0.254" layer="94"/>
<wire x1="10.16" y1="5.08" x2="10.16" y2="-5.08" width="0.254" layer="94"/>
<wire x1="10.16" y1="-5.08" x2="-10.16" y2="-5.08" width="0.254" layer="94"/>
<wire x1="-10.16" y1="-5.08" x2="-10.16" y2="5.08" width="0.254" layer="94"/>
<text x="-10.16" y="6.35" size="1.27" layer="95" font="vector">&gt;NAME</text>
<text x="-10.16" y="-7.62" size="1.27" layer="96" font="vector">&gt;VALUE</text>
<text x="-10.16" y="-10.16" size="1.27" layer="97" font="vector">&gt;PACKAGE</text>
</symbol>
</symbols>
<devicesets>
<deviceset name="AP2125" prefix="U" uservalue="yes">
<gates>
<gate name="G$1" symbol="AP2125" x="0" y="0"/>
</gates>
<devices>
<device name="FIXED" package="SOT23-3">
<connects>
<connect gate="G$1" pin="GND" pad="1"/>
<connect gate="G$1" pin="VIN" pad="3"/>
<connect gate="G$1" pin="VOUT" pad="2"/>
</connects>
<technologies>
<technology name="">
<attribute name="MPN" value="" constant="no"/>
<attribute name="PACKAGE" value="SOT23-3"/>
</technology>
</technologies>
</device>
</devices>
</deviceset>
</devicesets>
</library>
</libraries>
<attributes>
</attributes>
<variantdefs>
</variantdefs>
<classes>
<class number="0" name="NORMAL" width="0" drill="0">
</class>
<class number="1" name="USB_DIFF" width="0.254" drill="0">
<clearance class="1" value="0.1778"/>
</class>
</classes>
<parts>
<part name="Y1" library="USER_CRYSTALS" deviceset="CRYSTAL" device="FA-238" value="16 MHz">
<attribute name="MPN" value="FA-238 16.0000MB-C3"/>
</part>
<part name="C1" library="USER_SMT_CHIP_STANDARD" deviceset="C_SMD" device="C0603" value="18p">
<attribute name="MPN" value="C0603C180J5GACTU"/>
</part>
<part name="C2" library="USER_SMT_CHIP_STANDARD" deviceset="C_SMD" device="C0603" value="18p">
<attribute name="MPN" value="C0603C180J5GACTU"/>
</part>
<part name="GND1" library="supply1" library_urn="urn:adsk.eagle:library:371" deviceset="GND" device=""/>
<part name="CN1" library="USER_CON_PINS" deviceset="2X3_ICSP" device="ARDUINO_ICSP" value="2X3M">
<attribute name="MPN" value="PH2-06-UA"/>
</part>
<part name="GND2" library="supply1" library_urn="urn:adsk.eagle:library:371" deviceset="GND" device=""/>
<part name="C3" library="USER_SMT_CHIP_STANDARD" deviceset="C_SMD" device="C0603" value="0.1u">
<attribute name="MPN" value="CL10B104KB8NNNC"/>
</part>
<part name="C4" library="USER_SMT_CHIP_STANDARD" deviceset="C_SMD" device="C0603" value="0.1u">
<attribute name="MPN" value="CL10B104KB8NNNC"/>
</part>
<part name="GND3" library="supply1" library_urn="urn:adsk.eagle:library:371" deviceset="GND" device=""/>
<part name="R1" library="USER_SMT_CHIP_STANDARD" deviceset="R_SMD" device="R0603" value="10k">
<attribute name="MPN" value="ERJ-3EKF1002V"/>
</part>
<part name="D1" library="USER_DIODES" deviceset="SILICON" device="" value="1N4148WTR">
<attribute name="MPN" value="1N4148WTR"/>
</part>
<part name="GND4" library="supply1" library_urn="urn:adsk.eagle:library:371" deviceset="GND" device=""/>
<part name="C8" library="USER_SMT_CHIP_STANDARD" deviceset="C_SMD" device="C0603" value="1u">
<attribute name="MPN" value="CL10B105KP8NNNC"/>
</part>
<part name="R3" library="USER_SMT_CHIP_STANDARD" deviceset="R_SMD" device="R0603" value="22">
<attribute name="MPN" value="ERJ-3EKF22R0V"/>
</part>
<part name="R4" library="USER_SMT_CHIP_STANDARD" deviceset="R_SMD" device="R0603" value="22">
<attribute name="MPN" value="ERJ-3EKF22R0V"/>
</part>
<part name="U1" library="USER_AVR_MICROCONTROLLERS" deviceset="ATMEGA32U4" device="TQFP-44" value="ATMEGA32U4-AUR"/>
<part name="CN2" library="USER_CONN_USB" deviceset="USB_MICRO_B_GENERIC" device="SMT" value="10118192-0002LF">
<attribute name="MPN" value="10118192-0002LF"/>
</part>
<part name="GND5" library="supply1" library_urn="urn:adsk.eagle:library:371" deviceset="GND" device=""/>
<part name="R2" library="USER_SMT_CHIP_STANDARD" deviceset="R_SMD" device="R0603" value="10k">
<attribute name="MPN" value="ERJ-3EKF1002V"/>
</part>
<part name="GND6" library="supply1" library_urn="urn:adsk.eagle:library:371" deviceset="GND" device=""/>
<part name="U2" library="USER_PMIC" deviceset="AP2125" device="FIXED" value="AP2125N-3.3">
<attribute name="MPN" value="AP2125N-3.3TRG1"/>
</part>
<part name="R5" library="USER_SMT_CHIP_STANDARD" deviceset="R_SMD" device="R0603" value="0">
<attribute name="MPN" value="RMCF0603ZT0R00"/>
</part>
<part name="R6" library="USER_SMT_CHIP_STANDARD" deviceset="R_SMD" device="R0603" value="DNS"/>
<part name="GND7" library="supply1" library_urn="urn:adsk.eagle:library:371" deviceset="GND" device=""/>
<part name="C5" library="USER_SMT_CHIP_STANDARD" deviceset="C_SMD" device="C0603" value="0.1u">
<attribute name="MPN" value="CL10B104KB8NNNC"/>
</part>
<part name="C6" library="USER_SMT_CHIP_STANDARD" deviceset="C_SMD" device="C0603" value="0.1u">
<attribute name="MPN" value="CL10B104KB8NNNC"/>
</part>
<part name="C7" library="USER_SMT_CHIP_STANDARD" deviceset="C_SMD" device="C0603" value="1u">
<attribute name="MPN" value="CL10B105KP8NNNC"/>
</part>
<part name="C9" library="USER_SMT_CHIP_STANDARD" deviceset="C_SMD" device="C0603" value="1u">
<attribute name="MPN" value="CL10B105KP8NNNC"/>
</part>
<part name="R7" library="USER_SMT_CHIP_STANDARD" deviceset="R_SMD" device="R0603" value="DNS"/>
<part name="C10" library="USER_SMT_CHIP_STANDARD" deviceset="C_SMD" device="C0805" value="10u">
<attribute name="MPN" value="CL21A106KOFNNNE"/>
</part>
<part name="R8" library="USER_SMT_CHIP_STANDARD" deviceset="R_SMD" device="R0603" value="1k">
<attribute name="MPN" value="ERJ-3EKF1001V"/>
</part>
<part name="D2" library="USER_SMT_CHIP_STANDARD" deviceset="LED_SMD" device="" value="GREEN">
<attribute name="MPN" value="HSME-C191"/>
</part>
<part name="CN3" library="USER_CON_PINS" deviceset="1X6" device="THRU"/>
<part name="CN4" library="USER_CON_PINS" deviceset="1X6" device="THRU"/>
<part name="CN5" library="USER_CON_PINS" deviceset="1X11" device=""/>
<part name="CN6" library="USER_CON_PINS" deviceset="1X11" device=""/>
<part name="CN7" library="USER_CON_PINS" deviceset="1X11" device=""/>
<part name="J1" library="USER_CON_PINS" deviceset="1X2" device=""/>
<part name="R9" library="USER_SMT_CHIP_STANDARD" deviceset="R_SMD" device="R0603" value="1k">
<attribute name="MPN" value="ERJ-3EKF1001V"/>
</part>
<part name="D3" library="USER_SMT_CHIP_STANDARD" deviceset="LED_SMD" device="" value="RED">
<attribute name="MPN" value="ASMT-RR45-AQ902"/>
</part>
<part name="GND8" library="supply1" library_urn="urn:adsk.eagle:library:371" deviceset="GND" device=""/>
</parts>
<sheets>
<sheet>
<plain>
<text x="176.53" y="43.18" size="1.27" layer="91" font="vector" align="center-left">???</text>
</plain>
<instances>
<instance part="Y1" gate="G$1" x="86.36" y="26.67" smashed="yes">
<attribute name="NAME" x="86.36" y="33.02" size="1.27" layer="95" font="vector" align="bottom-center"/>
<attribute name="VALUE" x="86.36" y="30.48" size="1.27" layer="96" font="vector" align="bottom-center"/>
</instance>
<instance part="C1" gate="G$1" x="92.71" y="21.59" smashed="yes" rot="R90">
<attribute name="NAME" x="95.25" y="24.13" size="1.27" layer="95" font="vector"/>
<attribute name="VALUE" x="95.25" y="21.59" size="1.27" layer="96" font="vector"/>
<attribute name="PACKAGE" x="95.25" y="19.05" size="1.27" layer="97" font="vector"/>
</instance>
<instance part="C2" gate="G$1" x="80.01" y="21.59" smashed="yes" rot="R90">
<attribute name="NAME" x="77.47" y="25.4" size="1.27" layer="95" font="vector" rot="R180"/>
<attribute name="VALUE" x="77.47" y="22.86" size="1.27" layer="96" font="vector" rot="R180"/>
<attribute name="PACKAGE" x="77.47" y="20.32" size="1.27" layer="97" font="vector" rot="R180"/>
</instance>
<instance part="GND1" gate="1" x="96.52" y="12.7" smashed="yes">
<attribute name="VALUE" x="96.52" y="10.16" size="1.27" layer="96" font="vector" align="bottom-center"/>
</instance>
<instance part="CN1" gate="G$1" x="25.4" y="29.21" smashed="yes">
<attribute name="VALUE" x="15.24" y="16.51" size="1.27" layer="96" font="vector"/>
<attribute name="NAME" x="15.24" y="19.05" size="1.27" layer="95" font="vector"/>
</instance>
<instance part="GND2" gate="1" x="43.18" y="19.05" smashed="yes">
<attribute name="VALUE" x="43.18" y="16.51" size="1.27" layer="96" font="vector" align="bottom-center"/>
</instance>
<instance part="C3" gate="G$1" x="95.25" y="121.92" smashed="yes" rot="R90">
<attribute name="NAME" x="92.71" y="120.65" size="1.27" layer="95" font="vector" rot="R90"/>
<attribute name="VALUE" x="99.06" y="120.65" size="1.27" layer="96" font="vector" rot="R90"/>
<attribute name="PACKAGE" x="101.6" y="120.65" size="1.27" layer="97" font="vector" rot="R90"/>
</instance>
<instance part="C4" gate="G$1" x="106.68" y="121.92" smashed="yes" rot="R90">
<attribute name="NAME" x="104.14" y="120.65" size="1.27" layer="95" font="vector" rot="R90"/>
<attribute name="VALUE" x="110.49" y="120.65" size="1.27" layer="96" font="vector" rot="R90"/>
<attribute name="PACKAGE" x="113.03" y="120.65" size="1.27" layer="97" font="vector" rot="R90"/>
</instance>
<instance part="GND3" gate="1" x="113.03" y="114.3" smashed="yes">
<attribute name="VALUE" x="113.03" y="111.76" size="1.27" layer="96" font="vector" align="bottom-center"/>
</instance>
<instance part="R1" gate="G$1" x="76.2" y="49.53" smashed="yes" rot="R90">
<attribute name="NAME" x="78.74" y="52.07" size="1.27" layer="95" font="vector"/>
<attribute name="VALUE" x="78.74" y="49.53" size="1.27" layer="96" font="vector"/>
<attribute name="PACKAGE" x="78.74" y="46.99" size="1.27" layer="97" font="vector"/>
</instance>
<instance part="D1" gate="G$1" x="68.58" y="49.53" smashed="yes" rot="R90">
<attribute name="NAME" x="66.04" y="48.26" size="1.27" layer="95" font="vector" rot="R90"/>
<attribute name="VALUE" x="72.39" y="44.45" size="1.27" layer="96" font="vector" rot="R90"/>
</instance>
<instance part="GND4" gate="1" x="82.55" y="77.47" smashed="yes">
<attribute name="VALUE" x="82.55" y="74.93" size="1.27" layer="96" font="vector" align="bottom-center"/>
</instance>
<instance part="C8" gate="G$1" x="88.9" y="81.28" smashed="yes">
<attribute name="NAME" x="87.63" y="83.82" size="1.27" layer="95" font="vector"/>
<attribute name="VALUE" x="87.63" y="77.47" size="1.27" layer="96" font="vector"/>
<attribute name="PACKAGE" x="87.63" y="74.93" size="1.27" layer="97" font="vector"/>
</instance>
<instance part="R3" gate="G$1" x="74.93" y="73.66" smashed="yes">
<attribute name="NAME" x="73.66" y="74.93" size="1.27" layer="95" font="vector"/>
<attribute name="VALUE" x="73.66" y="71.12" size="1.27" layer="96" font="vector"/>
<attribute name="PACKAGE" x="73.66" y="68.58" size="1.27" layer="97" font="vector"/>
</instance>
<instance part="R4" gate="G$1" x="82.55" y="68.58" smashed="yes">
<attribute name="NAME" x="81.28" y="69.85" size="1.27" layer="95" font="vector"/>
<attribute name="VALUE" x="81.28" y="66.04" size="1.27" layer="96" font="vector"/>
<attribute name="PACKAGE" x="81.28" y="63.5" size="1.27" layer="97" font="vector"/>
</instance>
<instance part="U1" gate="G$1" x="137.16" y="58.42" smashed="yes">
<attribute name="NAME" x="114.3" y="104.14" size="1.27" layer="95" font="vector"/>
<attribute name="VALUE" x="114.3" y="12.7" size="1.27" layer="95" font="vector"/>
<attribute name="PACKAGE" x="114.3" y="10.16" size="1.27" layer="97" font="vector"/>
</instance>
<instance part="CN2" gate="G$1" x="11.43" y="69.85" smashed="yes" rot="MR0">
<attribute name="NAME" x="11.43" y="78.74" size="1.27" layer="95" font="vector" rot="MR0"/>
<attribute name="VALUE" x="11.43" y="59.69" size="1.27" layer="96" font="vector" rot="MR0"/>
</instance>
<instance part="GND5" gate="1" x="19.05" y="44.45" smashed="yes">
<attribute name="VALUE" x="19.05" y="41.91" size="1.27" layer="96" font="vector" align="bottom-center"/>
</instance>
<instance part="R2" gate="G$1" x="179.07" y="30.48" smashed="yes" rot="R90">
<attribute name="NAME" x="181.61" y="33.02" size="1.27" layer="95" font="vector"/>
<attribute name="VALUE" x="181.61" y="30.48" size="1.27" layer="96" font="vector"/>
<attribute name="PACKAGE" x="181.61" y="27.94" size="1.27" layer="97" font="vector"/>
</instance>
<instance part="GND6" gate="1" x="179.07" y="11.43" smashed="yes">
<attribute name="VALUE" x="179.07" y="8.89" size="1.27" layer="96" font="vector" align="bottom-center"/>
</instance>
<instance part="U2" gate="G$1" x="53.34" y="95.25" smashed="yes">
<attribute name="NAME" x="43.18" y="101.6" size="1.27" layer="95" font="vector"/>
<attribute name="VALUE" x="43.18" y="87.63" size="1.27" layer="96" font="vector"/>
<attribute name="PACKAGE" x="43.18" y="85.09" size="1.27" layer="97" font="vector"/>
</instance>
<instance part="R5" gate="G$1" x="93.98" y="100.33" smashed="yes" rot="R90">
<attribute name="NAME" x="91.44" y="99.06" size="1.27" layer="95" font="vector" rot="R90"/>
<attribute name="VALUE" x="97.79" y="99.06" size="1.27" layer="96" font="vector" rot="R90"/>
<attribute name="PACKAGE" x="100.33" y="99.06" size="1.27" layer="97" font="vector" rot="R90"/>
</instance>
<instance part="R6" gate="G$1" x="77.47" y="97.79" smashed="yes">
<attribute name="NAME" x="76.2" y="100.33" size="1.27" layer="95" font="vector"/>
<attribute name="VALUE" x="76.2" y="93.98" size="1.27" layer="96" font="vector"/>
<attribute name="PACKAGE" x="76.2" y="91.44" size="1.27" layer="97" font="vector"/>
</instance>
<instance part="GND7" gate="1" x="53.34" y="78.74" smashed="yes">
<attribute name="VALUE" x="53.34" y="76.2" size="1.27" layer="96" font="vector" align="bottom-center"/>
</instance>
<instance part="C5" gate="G$1" x="118.11" y="121.92" smashed="yes" rot="R90">
<attribute name="NAME" x="115.57" y="120.65" size="1.27" layer="95" font="vector" rot="R90"/>
<attribute name="VALUE" x="121.92" y="120.65" size="1.27" layer="96" font="vector" rot="R90"/>
<attribute name="PACKAGE" x="124.46" y="120.65" size="1.27" layer="97" font="vector" rot="R90"/>
</instance>
<instance part="C6" gate="G$1" x="129.54" y="121.92" smashed="yes" rot="R90">
<attribute name="NAME" x="127" y="120.65" size="1.27" layer="95" font="vector" rot="R90"/>
<attribute name="VALUE" x="133.35" y="120.65" size="1.27" layer="96" font="vector" rot="R90"/>
<attribute name="PACKAGE" x="135.89" y="120.65" size="1.27" layer="97" font="vector" rot="R90"/>
</instance>
<instance part="C7" gate="G$1" x="33.02" y="86.36" smashed="yes" rot="R90">
<attribute name="NAME" x="30.48" y="85.09" size="1.27" layer="95" font="vector" rot="R90"/>
<attribute name="VALUE" x="36.83" y="85.09" size="1.27" layer="96" font="vector" rot="R90"/>
<attribute name="PACKAGE" x="39.37" y="85.09" size="1.27" layer="97" font="vector" rot="R90"/>
</instance>
<instance part="C9" gate="G$1" x="71.12" y="86.36" smashed="yes" rot="R90">
<attribute name="NAME" x="68.58" y="85.09" size="1.27" layer="95" font="vector" rot="R90"/>
<attribute name="VALUE" x="74.93" y="85.09" size="1.27" layer="96" font="vector" rot="R90"/>
<attribute name="PACKAGE" x="77.47" y="85.09" size="1.27" layer="97" font="vector" rot="R90"/>
</instance>
<instance part="R7" gate="G$1" x="93.98" y="87.63" smashed="yes" rot="R90">
<attribute name="NAME" x="91.44" y="86.36" size="1.27" layer="95" font="vector" rot="R90"/>
<attribute name="VALUE" x="97.79" y="86.36" size="1.27" layer="96" font="vector" rot="R90"/>
<attribute name="PACKAGE" x="100.33" y="86.36" size="1.27" layer="97" font="vector" rot="R90"/>
</instance>
<instance part="C10" gate="G$1" x="26.67" y="60.96" smashed="yes" rot="R90">
<attribute name="NAME" x="24.13" y="59.69" size="1.27" layer="95" font="vector" rot="R90"/>
<attribute name="VALUE" x="30.48" y="59.69" size="1.27" layer="96" font="vector" rot="R90"/>
<attribute name="PACKAGE" x="33.02" y="59.69" size="1.27" layer="97" font="vector" rot="R90"/>
</instance>
<instance part="R8" gate="G$1" x="38.1" y="60.96" smashed="yes" rot="R90">
<attribute name="NAME" x="35.56" y="59.69" size="1.27" layer="95" font="vector" rot="R90"/>
<attribute name="VALUE" x="41.91" y="59.69" size="1.27" layer="96" font="vector" rot="R90"/>
<attribute name="PACKAGE" x="44.45" y="59.69" size="1.27" layer="97" font="vector" rot="R90"/>
</instance>
<instance part="D2" gate="G$1" x="38.1" y="53.34" smashed="yes" rot="R270">
<attribute name="NAME" x="35.56" y="52.07" size="1.27" layer="95" font="vector" rot="R90"/>
<attribute name="VALUE" x="44.45" y="50.8" size="1.27" layer="96" font="vector" rot="R90"/>
</instance>
<instance part="CN3" gate="G$1" x="204.47" y="87.63" smashed="yes" rot="R180">
<attribute name="NAME" x="207.01" y="71.12" size="1.27" layer="95" font="vector" rot="R180"/>
<attribute name="VALUE" x="207.01" y="105.41" size="1.27" layer="96" font="vector" rot="R180"/>
</instance>
<instance part="CN4" gate="G$1" x="204.47" y="49.53" smashed="yes" rot="R180">
<attribute name="NAME" x="207.01" y="33.02" size="1.27" layer="95" font="vector" rot="R180"/>
<attribute name="VALUE" x="207.01" y="67.31" size="1.27" layer="96" font="vector" rot="R180"/>
</instance>
<instance part="CN5" gate="G$1" x="255.27" y="11.43" smashed="yes" rot="MR270">
<attribute name="NAME" x="226.06" y="13.97" size="1.27" layer="95" font="vector" rot="MR270"/>
<attribute name="VALUE" x="285.75" y="13.97" size="1.27" layer="96" font="vector" rot="MR270"/>
</instance>
<instance part="CN6" gate="G$1" x="306.07" y="68.58" smashed="yes" rot="MR180">
<attribute name="NAME" x="303.53" y="39.37" size="1.27" layer="95" font="vector" rot="MR180"/>
<attribute name="VALUE" x="303.53" y="99.06" size="1.27" layer="96" font="vector" rot="MR180"/>
</instance>
<instance part="CN7" gate="G$1" x="255.27" y="125.73" smashed="yes" rot="MR90">
<attribute name="NAME" x="284.48" y="123.19" size="1.27" layer="95" font="vector" rot="MR90"/>
<attribute name="VALUE" x="224.79" y="123.19" size="1.27" layer="96" font="vector" rot="MR90"/>
</instance>
<instance part="J1" gate="G$1" x="63.5" y="30.48" smashed="yes" rot="MR0">
<attribute name="NAME" x="63.5" y="36.83" size="1.27" layer="95" font="vector" rot="MR0"/>
<attribute name="VALUE" x="63.5" y="22.86" size="1.27" layer="96" font="vector" rot="MR0"/>
</instance>
<instance part="R9" gate="G$1" x="322.58" y="90.17" smashed="yes" rot="R90">
<attribute name="NAME" x="320.04" y="88.9" size="1.27" layer="95" font="vector" rot="R90"/>
<attribute name="VALUE" x="326.39" y="88.9" size="1.27" layer="96" font="vector" rot="R90"/>
<attribute name="PACKAGE" x="328.93" y="88.9" size="1.27" layer="97" font="vector" rot="R90"/>
</instance>
<instance part="D3" gate="G$1" x="322.58" y="82.55" smashed="yes" rot="R270">
<attribute name="NAME" x="320.04" y="81.28" size="1.27" layer="95" font="vector" rot="R90"/>
<attribute name="VALUE" x="328.93" y="80.01" size="1.27" layer="96" font="vector" rot="R90"/>
</instance>
<instance part="GND8" gate="1" x="322.58" y="74.93" smashed="yes">
<attribute name="VALUE" x="322.58" y="72.39" size="1.27" layer="96" font="vector" align="bottom-center"/>
</instance>
</instances>
<busses>
</busses>
<nets>
<net name="N$1" class="0">
<segment>
<pinref part="Y1" gate="G$1" pin="1"/>
<wire x1="82.55" y1="26.67" x2="80.01" y2="26.67" width="0.1524" layer="91"/>
<pinref part="C2" gate="G$1" pin="P$2"/>
<wire x1="80.01" y1="26.67" x2="80.01" y2="25.4" width="0.1524" layer="91"/>
<wire x1="80.01" y1="26.67" x2="80.01" y2="36.83" width="0.1524" layer="91"/>
<junction x="80.01" y="26.67"/>
<pinref part="U1" gate="G$1" pin="XTAL2"/>
<wire x1="109.22" y1="38.1" x2="81.28" y2="38.1" width="0.1524" layer="91"/>
<wire x1="81.28" y1="38.1" x2="80.01" y2="36.83" width="0.1524" layer="91"/>
</segment>
</net>
<net name="GND" class="0">
<segment>
<pinref part="CN1" gate="G$1" pin="GND"/>
<wire x1="40.64" y1="24.13" x2="43.18" y2="24.13" width="0.1524" layer="91"/>
<wire x1="43.18" y1="24.13" x2="43.18" y2="21.59" width="0.1524" layer="91"/>
<pinref part="GND2" gate="1" pin="GND"/>
</segment>
<segment>
<pinref part="C2" gate="G$1" pin="P$1"/>
<wire x1="80.01" y1="19.05" x2="80.01" y2="17.78" width="0.1524" layer="91"/>
<wire x1="80.01" y1="17.78" x2="83.82" y2="17.78" width="0.1524" layer="91"/>
<pinref part="C1" gate="G$1" pin="P$1"/>
<wire x1="83.82" y1="17.78" x2="88.9" y2="17.78" width="0.1524" layer="91"/>
<wire x1="88.9" y1="17.78" x2="92.71" y2="17.78" width="0.1524" layer="91"/>
<wire x1="92.71" y1="17.78" x2="92.71" y2="19.05" width="0.1524" layer="91"/>
<pinref part="Y1" gate="G$1" pin="GND@2"/>
<wire x1="83.82" y1="20.32" x2="83.82" y2="17.78" width="0.1524" layer="91"/>
<junction x="83.82" y="17.78"/>
<pinref part="Y1" gate="G$1" pin="GND@4"/>
<wire x1="88.9" y1="20.32" x2="88.9" y2="17.78" width="0.1524" layer="91"/>
<junction x="88.9" y="17.78"/>
<pinref part="U1" gate="G$1" pin="GND@43"/>
<wire x1="109.22" y1="17.78" x2="106.68" y2="17.78" width="0.1524" layer="91"/>
<junction x="92.71" y="17.78"/>
<pinref part="U1" gate="G$1" pin="USB_GND"/>
<wire x1="106.68" y1="17.78" x2="96.52" y2="17.78" width="0.1524" layer="91"/>
<wire x1="96.52" y1="17.78" x2="92.71" y2="17.78" width="0.1524" layer="91"/>
<wire x1="109.22" y1="27.94" x2="106.68" y2="27.94" width="0.1524" layer="91"/>
<wire x1="106.68" y1="27.94" x2="106.68" y2="25.4" width="0.1524" layer="91"/>
<junction x="106.68" y="17.78"/>
<pinref part="U1" gate="G$1" pin="GND@35"/>
<wire x1="106.68" y1="25.4" x2="106.68" y2="22.86" width="0.1524" layer="91"/>
<wire x1="106.68" y1="22.86" x2="106.68" y2="20.32" width="0.1524" layer="91"/>
<wire x1="106.68" y1="20.32" x2="106.68" y2="17.78" width="0.1524" layer="91"/>
<wire x1="109.22" y1="20.32" x2="106.68" y2="20.32" width="0.1524" layer="91"/>
<junction x="106.68" y="20.32"/>
<pinref part="U1" gate="G$1" pin="GND@23"/>
<wire x1="109.22" y1="22.86" x2="106.68" y2="22.86" width="0.1524" layer="91"/>
<junction x="106.68" y="22.86"/>
<pinref part="U1" gate="G$1" pin="GND@15"/>
<wire x1="109.22" y1="25.4" x2="106.68" y2="25.4" width="0.1524" layer="91"/>
<junction x="106.68" y="25.4"/>
<pinref part="GND1" gate="1" pin="GND"/>
<wire x1="96.52" y1="15.24" x2="96.52" y2="17.78" width="0.1524" layer="91"/>
<junction x="96.52" y="17.78"/>
<wire x1="68.58" y1="27.94" x2="68.58" y2="17.78" width="0.1524" layer="91"/>
<wire x1="68.58" y1="17.78" x2="80.01" y2="17.78" width="0.1524" layer="91"/>
<junction x="80.01" y="17.78"/>
<pinref part="J1" gate="G$1" pin="2"/>
</segment>
<segment>
<pinref part="CN2" gate="G$1" pin="GND"/>
<wire x1="16.51" y1="64.77" x2="19.05" y2="64.77" width="0.1524" layer="91"/>
<pinref part="GND5" gate="1" pin="GND"/>
<wire x1="19.05" y1="64.77" x2="19.05" y2="54.61" width="0.1524" layer="91"/>
<pinref part="CN2" gate="G$1" pin="SHELL"/>
<wire x1="19.05" y1="54.61" x2="19.05" y2="48.26" width="0.1524" layer="91"/>
<wire x1="19.05" y1="48.26" x2="19.05" y2="46.99" width="0.1524" layer="91"/>
<wire x1="16.51" y1="54.61" x2="19.05" y2="54.61" width="0.1524" layer="91"/>
<junction x="19.05" y="54.61"/>
<pinref part="C10" gate="G$1" pin="P$1"/>
<wire x1="26.67" y1="58.42" x2="26.67" y2="54.61" width="0.1524" layer="91"/>
<wire x1="26.67" y1="54.61" x2="19.05" y2="54.61" width="0.1524" layer="91"/>
<pinref part="D2" gate="G$1" pin="C"/>
<wire x1="38.1" y1="49.53" x2="38.1" y2="48.26" width="0.1524" layer="91"/>
<wire x1="38.1" y1="48.26" x2="19.05" y2="48.26" width="0.1524" layer="91"/>
<junction x="19.05" y="48.26"/>
</segment>
<segment>
<pinref part="GND6" gate="1" pin="GND"/>
<pinref part="R2" gate="G$1" pin="P$1"/>
<wire x1="179.07" y1="13.97" x2="179.07" y2="27.94" width="0.1524" layer="91"/>
</segment>
<segment>
<pinref part="C8" gate="G$1" pin="P$1"/>
<wire x1="86.36" y1="81.28" x2="82.55" y2="81.28" width="0.1524" layer="91"/>
<pinref part="GND4" gate="1" pin="GND"/>
<wire x1="82.55" y1="81.28" x2="82.55" y2="80.01" width="0.1524" layer="91"/>
</segment>
<segment>
<pinref part="U2" gate="G$1" pin="GND"/>
<pinref part="GND7" gate="1" pin="GND"/>
<wire x1="53.34" y1="85.09" x2="53.34" y2="82.55" width="0.1524" layer="91"/>
<pinref part="C7" gate="G$1" pin="P$1"/>
<wire x1="53.34" y1="82.55" x2="53.34" y2="81.28" width="0.1524" layer="91"/>
<wire x1="33.02" y1="83.82" x2="33.02" y2="82.55" width="0.1524" layer="91"/>
<wire x1="33.02" y1="82.55" x2="53.34" y2="82.55" width="0.1524" layer="91"/>
<junction x="53.34" y="82.55"/>
<pinref part="C9" gate="G$1" pin="P$1"/>
<wire x1="71.12" y1="83.82" x2="71.12" y2="82.55" width="0.1524" layer="91"/>
<wire x1="71.12" y1="82.55" x2="53.34" y2="82.55" width="0.1524" layer="91"/>
</segment>
<segment>
<pinref part="C3" gate="G$1" pin="P$1"/>
<wire x1="95.25" y1="119.38" x2="95.25" y2="118.11" width="0.1524" layer="91"/>
<wire x1="95.25" y1="118.11" x2="106.68" y2="118.11" width="0.1524" layer="91"/>
<pinref part="C6" gate="G$1" pin="P$1"/>
<wire x1="106.68" y1="118.11" x2="113.03" y2="118.11" width="0.1524" layer="91"/>
<wire x1="113.03" y1="118.11" x2="118.11" y2="118.11" width="0.1524" layer="91"/>
<wire x1="118.11" y1="118.11" x2="129.54" y2="118.11" width="0.1524" layer="91"/>
<wire x1="129.54" y1="118.11" x2="129.54" y2="119.38" width="0.1524" layer="91"/>
<pinref part="C5" gate="G$1" pin="P$1"/>
<wire x1="118.11" y1="119.38" x2="118.11" y2="118.11" width="0.1524" layer="91"/>
<junction x="118.11" y="118.11"/>
<pinref part="C4" gate="G$1" pin="P$1"/>
<wire x1="106.68" y1="119.38" x2="106.68" y2="118.11" width="0.1524" layer="91"/>
<junction x="106.68" y="118.11"/>
<pinref part="GND3" gate="1" pin="GND"/>
<wire x1="113.03" y1="116.84" x2="113.03" y2="118.11" width="0.1524" layer="91"/>
<junction x="113.03" y="118.11"/>
</segment>
<segment>
<pinref part="CN3" gate="G$1" pin="2"/>
<wire x1="209.55" y1="80.01" x2="212.09" y2="80.01" width="0.1524" layer="91"/>
<label x="212.09" y="80.01" size="1.27" layer="95" font="vector" xref="yes"/>
</segment>
<segment>
<pinref part="CN5" gate="G$1" pin="4"/>
<wire x1="245.11" y1="16.51" x2="245.11" y2="19.05" width="0.1524" layer="91"/>
<label x="245.11" y="19.05" size="1.27" layer="95" font="vector" rot="R90" xref="yes"/>
</segment>
<segment>
<pinref part="CN6" gate="G$1" pin="1"/>
<wire x1="300.99" y1="43.18" x2="298.45" y2="43.18" width="0.1524" layer="91"/>
<label x="298.45" y="43.18" size="1.27" layer="95" font="vector" rot="R180" xref="yes"/>
</segment>
<segment>
<pinref part="CN4" gate="G$1" pin="5"/>
<wire x1="209.55" y1="57.15" x2="212.09" y2="57.15" width="0.1524" layer="91"/>
<label x="212.09" y="57.15" size="1.27" layer="95" font="vector" xref="yes"/>
</segment>
<segment>
<pinref part="CN7" gate="G$1" pin="2"/>
<wire x1="275.59" y1="120.65" x2="275.59" y2="118.11" width="0.1524" layer="91"/>
<label x="275.59" y="118.11" size="1.27" layer="95" font="vector" rot="R270" xref="yes"/>
</segment>
<segment>
<pinref part="CN7" gate="G$1" pin="10"/>
<wire x1="234.95" y1="120.65" x2="234.95" y2="118.11" width="0.1524" layer="91"/>
<label x="234.95" y="118.11" size="1.27" layer="95" font="vector" rot="R270" xref="yes"/>
</segment>
<segment>
<pinref part="D3" gate="G$1" pin="C"/>
<wire x1="322.58" y1="78.74" x2="322.58" y2="77.47" width="0.1524" layer="91"/>
<pinref part="GND8" gate="1" pin="GND"/>
</segment>
<segment>
<pinref part="CN5" gate="G$1" pin="5"/>
<wire x1="250.19" y1="16.51" x2="250.19" y2="19.05" width="0.1524" layer="91"/>
<label x="250.19" y="19.05" size="1.27" layer="95" font="vector" rot="R90" xref="yes"/>
</segment>
<segment>
<pinref part="CN5" gate="G$1" pin="6"/>
<wire x1="255.27" y1="16.51" x2="255.27" y2="19.05" width="0.1524" layer="91"/>
<label x="255.27" y="19.05" size="1.27" layer="95" font="vector" rot="R90" xref="yes"/>
</segment>
</net>
<net name="N$4" class="0">
<segment>
<pinref part="C1" gate="G$1" pin="P$2"/>
<pinref part="Y1" gate="G$1" pin="3"/>
<wire x1="90.17" y1="26.67" x2="92.71" y2="26.67" width="0.1524" layer="91"/>
<wire x1="92.71" y1="26.67" x2="92.71" y2="25.4" width="0.1524" layer="91"/>
<pinref part="U1" gate="G$1" pin="XTAL1"/>
<wire x1="109.22" y1="33.02" x2="93.98" y2="33.02" width="0.1524" layer="91"/>
<wire x1="93.98" y1="33.02" x2="92.71" y2="31.75" width="0.1524" layer="91"/>
<wire x1="92.71" y1="31.75" x2="92.71" y2="26.67" width="0.1524" layer="91"/>
<junction x="92.71" y="26.67"/>
</segment>
</net>
<net name="!RST" class="0">
<segment>
<pinref part="CN1" gate="G$1" pin="RST"/>
<wire x1="10.16" y1="24.13" x2="7.62" y2="24.13" width="0.1524" layer="91"/>
<label x="7.62" y="24.13" size="1.27" layer="95" font="vector" rot="R180" xref="yes"/>
</segment>
<segment>
<label x="66.04" y="43.18" size="1.27" layer="95" font="vector" rot="R180" xref="yes"/>
<pinref part="R1" gate="G$1" pin="P$1"/>
<wire x1="76.2" y1="43.18" x2="68.58" y2="43.18" width="0.1524" layer="91"/>
<wire x1="68.58" y1="43.18" x2="66.04" y2="43.18" width="0.1524" layer="91"/>
<wire x1="76.2" y1="46.99" x2="76.2" y2="43.18" width="0.1524" layer="91"/>
<pinref part="D1" gate="G$1" pin="A"/>
<wire x1="68.58" y1="45.72" x2="68.58" y2="43.18" width="0.1524" layer="91"/>
<junction x="68.58" y="43.18"/>
<wire x1="68.58" y1="33.02" x2="68.58" y2="43.18" width="0.1524" layer="91"/>
<pinref part="U1" gate="G$1" pin="!RESET"/>
<wire x1="109.22" y1="43.18" x2="76.2" y2="43.18" width="0.1524" layer="91"/>
<junction x="76.2" y="43.18"/>
<pinref part="J1" gate="G$1" pin="1"/>
</segment>
<segment>
<pinref part="CN5" gate="G$1" pin="2"/>
<wire x1="234.95" y1="16.51" x2="234.95" y2="19.05" width="0.1524" layer="91"/>
<label x="234.95" y="19.05" size="1.27" layer="95" font="vector" rot="R90" xref="yes"/>
</segment>
</net>
<net name="D_N" class="1">
<segment>
<pinref part="U1" gate="G$1" pin="D-"/>
<pinref part="R3" gate="G$1" pin="P$2"/>
<wire x1="109.22" y1="73.66" x2="78.74" y2="73.66" width="0.1524" layer="91"/>
</segment>
</net>
<net name="D_P" class="1">
<segment>
<pinref part="U1" gate="G$1" pin="D+"/>
<pinref part="R4" gate="G$1" pin="P$2"/>
<wire x1="109.22" y1="68.58" x2="86.36" y2="68.58" width="0.1524" layer="91"/>
</segment>
</net>
<net name="USB_D_N" class="1">
<segment>
<pinref part="R3" gate="G$1" pin="P$1"/>
<wire x1="72.39" y1="73.66" x2="38.1" y2="73.66" width="0.1524" layer="91"/>
<wire x1="38.1" y1="73.66" x2="36.83" y2="72.39" width="0.1524" layer="91"/>
<pinref part="CN2" gate="G$1" pin="D-"/>
<wire x1="36.83" y1="72.39" x2="16.51" y2="72.39" width="0.1524" layer="91"/>
<label x="17.78" y="72.39" size="1.27" layer="95" font="vector"/>
</segment>
</net>
<net name="USB_D_P" class="1">
<segment>
<pinref part="CN2" gate="G$1" pin="D+"/>
<wire x1="16.51" y1="69.85" x2="36.83" y2="69.85" width="0.1524" layer="91"/>
<pinref part="R4" gate="G$1" pin="P$1"/>
<wire x1="36.83" y1="69.85" x2="38.1" y2="68.58" width="0.1524" layer="91"/>
<wire x1="38.1" y1="68.58" x2="80.01" y2="68.58" width="0.1524" layer="91"/>
<label x="17.78" y="69.85" size="1.27" layer="95" font="vector"/>
</segment>
</net>
<net name="AREF" class="0">
<segment>
<pinref part="U1" gate="G$1" pin="AREF"/>
<wire x1="109.22" y1="55.88" x2="106.68" y2="55.88" width="0.1524" layer="91"/>
<label x="106.68" y="55.88" size="1.27" layer="95" font="vector" rot="R180" xref="yes"/>
</segment>
<segment>
<pinref part="CN7" gate="G$1" pin="9"/>
<wire x1="240.03" y1="120.65" x2="240.03" y2="118.11" width="0.1524" layer="91"/>
<label x="240.03" y="118.11" size="1.27" layer="95" font="vector" rot="R270" xref="yes"/>
</segment>
</net>
<net name="N$3" class="0">
<segment>
<pinref part="U1" gate="G$1" pin="USB_CAP"/>
<pinref part="C8" gate="G$1" pin="P$2"/>
<wire x1="109.22" y1="81.28" x2="93.98" y2="81.28" width="0.1524" layer="91"/>
<pinref part="R7" gate="G$1" pin="P$1"/>
<wire x1="93.98" y1="81.28" x2="92.71" y2="81.28" width="0.1524" layer="91"/>
<wire x1="93.98" y1="85.09" x2="93.98" y2="81.28" width="0.1524" layer="91"/>
<junction x="93.98" y="81.28"/>
</segment>
</net>
<net name="USB_+5V" class="0">
<segment>
<pinref part="CN2" gate="G$1" pin="VBUS"/>
<wire x1="16.51" y1="74.93" x2="26.67" y2="74.93" width="0.1524" layer="91"/>
<wire x1="26.67" y1="74.93" x2="26.67" y2="97.79" width="0.1524" layer="91"/>
<pinref part="U1" gate="G$1" pin="USB_VCC"/>
<wire x1="26.67" y1="97.79" x2="26.67" y2="107.95" width="0.1524" layer="91"/>
<wire x1="109.22" y1="99.06" x2="106.68" y2="99.06" width="0.1524" layer="91"/>
<pinref part="U1" gate="G$1" pin="VBUS"/>
<wire x1="106.68" y1="99.06" x2="106.68" y2="107.95" width="0.1524" layer="91"/>
<wire x1="106.68" y1="107.95" x2="93.98" y2="107.95" width="0.1524" layer="91"/>
<wire x1="93.98" y1="107.95" x2="26.67" y2="107.95" width="0.1524" layer="91"/>
<wire x1="109.22" y1="96.52" x2="106.68" y2="96.52" width="0.1524" layer="91"/>
<wire x1="106.68" y1="96.52" x2="106.68" y2="99.06" width="0.1524" layer="91"/>
<junction x="106.68" y="99.06"/>
<label x="106.68" y="107.95" size="1.27" layer="95" font="vector" rot="MR0"/>
<label x="17.78" y="74.93" size="1.27" layer="95" font="vector"/>
<pinref part="R5" gate="G$1" pin="P$2"/>
<wire x1="93.98" y1="104.14" x2="93.98" y2="107.95" width="0.1524" layer="91"/>
<junction x="93.98" y="107.95"/>
<pinref part="U2" gate="G$1" pin="VIN"/>
<wire x1="38.1" y1="97.79" x2="33.02" y2="97.79" width="0.1524" layer="91"/>
<junction x="26.67" y="97.79"/>
<pinref part="C7" gate="G$1" pin="P$2"/>
<wire x1="33.02" y1="97.79" x2="26.67" y2="97.79" width="0.1524" layer="91"/>
<wire x1="33.02" y1="90.17" x2="33.02" y2="97.79" width="0.1524" layer="91"/>
<junction x="33.02" y="97.79"/>
<pinref part="C10" gate="G$1" pin="P$2"/>
<wire x1="26.67" y1="64.77" x2="26.67" y2="66.04" width="0.1524" layer="91"/>
<junction x="26.67" y="74.93"/>
<pinref part="R8" gate="G$1" pin="P$2"/>
<wire x1="26.67" y1="66.04" x2="26.67" y2="74.93" width="0.1524" layer="91"/>
<wire x1="38.1" y1="64.77" x2="38.1" y2="66.04" width="0.1524" layer="91"/>
<wire x1="38.1" y1="66.04" x2="26.67" y2="66.04" width="0.1524" layer="91"/>
<junction x="26.67" y="66.04"/>
</segment>
<segment>
<pinref part="CN3" gate="G$1" pin="5"/>
<wire x1="209.55" y1="95.25" x2="212.09" y2="95.25" width="0.1524" layer="91"/>
<label x="212.09" y="95.25" size="1.27" layer="95" font="vector" xref="yes"/>
</segment>
<segment>
<pinref part="CN3" gate="G$1" pin="1"/>
<wire x1="209.55" y1="74.93" x2="212.09" y2="74.93" width="0.1524" layer="91"/>
<label x="212.09" y="74.93" size="1.27" layer="95" font="vector" xref="yes"/>
</segment>
<segment>
<pinref part="CN4" gate="G$1" pin="6"/>
<wire x1="209.55" y1="62.23" x2="212.09" y2="62.23" width="0.1524" layer="91"/>
<label x="212.09" y="62.23" size="1.27" layer="95" font="vector" xref="yes"/>
</segment>
</net>
<net name="VCC_&amp;_AVCC" class="0">
<segment>
<pinref part="R5" gate="G$1" pin="P$1"/>
<wire x1="93.98" y1="97.79" x2="93.98" y2="93.98" width="0.1524" layer="91"/>
<wire x1="87.63" y1="93.98" x2="93.98" y2="93.98" width="0.1524" layer="91"/>
<junction x="93.98" y="93.98"/>
<pinref part="U1" gate="G$1" pin="VCC@14"/>
<wire x1="109.22" y1="93.98" x2="107.95" y2="93.98" width="0.1524" layer="91"/>
<pinref part="U1" gate="G$1" pin="AVCC@44"/>
<wire x1="107.95" y1="93.98" x2="93.98" y2="93.98" width="0.1524" layer="91"/>
<wire x1="109.22" y1="86.36" x2="107.95" y2="86.36" width="0.1524" layer="91"/>
<wire x1="107.95" y1="86.36" x2="107.95" y2="88.9" width="0.1524" layer="91"/>
<junction x="107.95" y="93.98"/>
<pinref part="U1" gate="G$1" pin="AVCC@24"/>
<wire x1="107.95" y1="88.9" x2="107.95" y2="91.44" width="0.1524" layer="91"/>
<wire x1="107.95" y1="91.44" x2="107.95" y2="93.98" width="0.1524" layer="91"/>
<wire x1="109.22" y1="88.9" x2="107.95" y2="88.9" width="0.1524" layer="91"/>
<junction x="107.95" y="88.9"/>
<pinref part="U1" gate="G$1" pin="VCC@34"/>
<wire x1="109.22" y1="91.44" x2="107.95" y2="91.44" width="0.1524" layer="91"/>
<junction x="107.95" y="91.44"/>
<pinref part="R6" gate="G$1" pin="P$2"/>
<wire x1="81.28" y1="97.79" x2="87.63" y2="97.79" width="0.1524" layer="91"/>
<wire x1="87.63" y1="97.79" x2="87.63" y2="93.98" width="0.1524" layer="91"/>
<label x="106.68" y="93.98" size="1.27" layer="95" font="vector" rot="MR0"/>
<pinref part="R7" gate="G$1" pin="P$2"/>
<wire x1="93.98" y1="91.44" x2="93.98" y2="93.98" width="0.1524" layer="91"/>
</segment>
<segment>
<pinref part="C3" gate="G$1" pin="P$2"/>
<wire x1="95.25" y1="125.73" x2="95.25" y2="127" width="0.1524" layer="91"/>
<wire x1="95.25" y1="127" x2="106.68" y2="127" width="0.1524" layer="91"/>
<pinref part="C6" gate="G$1" pin="P$2"/>
<wire x1="106.68" y1="127" x2="118.11" y2="127" width="0.1524" layer="91"/>
<wire x1="118.11" y1="127" x2="129.54" y2="127" width="0.1524" layer="91"/>
<wire x1="129.54" y1="127" x2="129.54" y2="125.73" width="0.1524" layer="91"/>
<pinref part="C5" gate="G$1" pin="P$2"/>
<wire x1="118.11" y1="125.73" x2="118.11" y2="127" width="0.1524" layer="91"/>
<junction x="118.11" y="127"/>
<pinref part="C4" gate="G$1" pin="P$2"/>
<wire x1="106.68" y1="125.73" x2="106.68" y2="127" width="0.1524" layer="91"/>
<junction x="106.68" y="127"/>
<wire x1="95.25" y1="127" x2="92.71" y2="127" width="0.1524" layer="91"/>
<junction x="95.25" y="127"/>
<label x="92.71" y="127" size="1.27" layer="95" font="vector" rot="R180" xref="yes"/>
</segment>
<segment>
<pinref part="CN5" gate="G$1" pin="3"/>
<wire x1="240.03" y1="16.51" x2="240.03" y2="19.05" width="0.1524" layer="91"/>
<label x="240.03" y="19.05" size="1.27" layer="95" font="vector" rot="R90" xref="yes"/>
</segment>
<segment>
<pinref part="CN6" gate="G$1" pin="2"/>
<wire x1="300.99" y1="48.26" x2="298.45" y2="48.26" width="0.1524" layer="91"/>
<label x="298.45" y="48.26" size="1.27" layer="95" font="vector" rot="R180" xref="yes"/>
</segment>
<segment>
<pinref part="CN7" gate="G$1" pin="1"/>
<wire x1="280.67" y1="120.65" x2="280.67" y2="118.11" width="0.1524" layer="91"/>
<label x="280.67" y="118.11" size="1.27" layer="95" font="vector" rot="R270" xref="yes"/>
</segment>
<segment>
<pinref part="CN7" gate="G$1" pin="11"/>
<wire x1="229.87" y1="120.65" x2="229.87" y2="118.11" width="0.1524" layer="91"/>
<label x="229.87" y="118.11" size="1.27" layer="95" font="vector" rot="R270" xref="yes"/>
</segment>
<segment>
<pinref part="R1" gate="G$1" pin="P$2"/>
<wire x1="76.2" y1="53.34" x2="76.2" y2="55.88" width="0.1524" layer="91"/>
<wire x1="76.2" y1="55.88" x2="68.58" y2="55.88" width="0.1524" layer="91"/>
<pinref part="D1" gate="G$1" pin="C"/>
<wire x1="68.58" y1="55.88" x2="68.58" y2="53.34" width="0.1524" layer="91"/>
<label x="66.04" y="55.88" size="1.27" layer="95" font="vector" rot="R180" xref="yes"/>
<wire x1="66.04" y1="55.88" x2="68.58" y2="55.88" width="0.1524" layer="91"/>
<junction x="68.58" y="55.88"/>
</segment>
<segment>
<pinref part="CN1" gate="G$1" pin="VCC"/>
<wire x1="40.64" y1="34.29" x2="43.18" y2="34.29" width="0.1524" layer="91"/>
<label x="43.18" y="34.29" size="1.27" layer="95" font="vector" xref="yes"/>
</segment>
</net>
<net name="N$7" class="0">
<segment>
<pinref part="R8" gate="G$1" pin="P$1"/>
<pinref part="D2" gate="G$1" pin="A"/>
<wire x1="38.1" y1="58.42" x2="38.1" y2="57.15" width="0.1524" layer="91"/>
</segment>
</net>
<net name="+3V3" class="0">
<segment>
<pinref part="U2" gate="G$1" pin="VOUT"/>
<pinref part="R6" gate="G$1" pin="P$1"/>
<wire x1="68.58" y1="97.79" x2="71.12" y2="97.79" width="0.1524" layer="91"/>
<pinref part="C9" gate="G$1" pin="P$2"/>
<wire x1="71.12" y1="97.79" x2="74.93" y2="97.79" width="0.1524" layer="91"/>
<wire x1="71.12" y1="90.17" x2="71.12" y2="97.79" width="0.1524" layer="91"/>
<junction x="71.12" y="97.79"/>
<label x="71.12" y="99.06" size="1.27" layer="95" font="vector" rot="R90" xref="yes"/>
</segment>
</net>
<net name="PF7" class="0">
<segment>
<pinref part="U1" gate="G$1" pin="PF7/ADC7/TDI"/>
<wire x1="167.64" y1="35.56" x2="170.18" y2="35.56" width="0.1524" layer="91"/>
<label x="170.18" y="35.56" size="1.27" layer="95" font="vector" xref="yes"/>
</segment>
<segment>
<pinref part="CN7" gate="G$1" pin="3"/>
<wire x1="270.51" y1="120.65" x2="270.51" y2="118.11" width="0.1524" layer="91"/>
<label x="270.51" y="118.11" size="1.27" layer="95" font="vector" rot="R270" xref="yes"/>
</segment>
</net>
<net name="PF6" class="0">
<segment>
<pinref part="U1" gate="G$1" pin="PF6/ADC6/TDO"/>
<wire x1="167.64" y1="33.02" x2="170.18" y2="33.02" width="0.1524" layer="91"/>
<label x="170.18" y="33.02" size="1.27" layer="95" font="vector" xref="yes"/>
</segment>
<segment>
<pinref part="CN7" gate="G$1" pin="4"/>
<wire x1="265.43" y1="120.65" x2="265.43" y2="118.11" width="0.1524" layer="91"/>
<label x="265.43" y="118.11" size="1.27" layer="95" font="vector" rot="R270" xref="yes"/>
</segment>
</net>
<net name="PF5" class="0">
<segment>
<pinref part="U1" gate="G$1" pin="PF5/ADC5/TMS"/>
<wire x1="167.64" y1="30.48" x2="170.18" y2="30.48" width="0.1524" layer="91"/>
<label x="170.18" y="30.48" size="1.27" layer="95" font="vector" xref="yes"/>
</segment>
<segment>
<pinref part="CN7" gate="G$1" pin="5"/>
<wire x1="260.35" y1="120.65" x2="260.35" y2="118.11" width="0.1524" layer="91"/>
<label x="260.35" y="118.11" size="1.27" layer="95" font="vector" rot="R270" xref="yes"/>
</segment>
</net>
<net name="PF4" class="0">
<segment>
<pinref part="U1" gate="G$1" pin="PF4/ADC4/TCK"/>
<wire x1="167.64" y1="27.94" x2="170.18" y2="27.94" width="0.1524" layer="91"/>
<label x="170.18" y="27.94" size="1.27" layer="95" font="vector" xref="yes"/>
</segment>
<segment>
<pinref part="CN7" gate="G$1" pin="6"/>
<wire x1="255.27" y1="120.65" x2="255.27" y2="118.11" width="0.1524" layer="91"/>
<label x="255.27" y="118.11" size="1.27" layer="95" font="vector" rot="R270" xref="yes"/>
</segment>
</net>
<net name="PF1" class="0">
<segment>
<pinref part="U1" gate="G$1" pin="PF1/ADC1"/>
<wire x1="167.64" y1="20.32" x2="170.18" y2="20.32" width="0.1524" layer="91"/>
<label x="170.18" y="20.32" size="1.27" layer="95" font="vector" xref="yes"/>
</segment>
<segment>
<pinref part="CN7" gate="G$1" pin="7"/>
<wire x1="250.19" y1="120.65" x2="250.19" y2="118.11" width="0.1524" layer="91"/>
<label x="250.19" y="118.11" size="1.27" layer="95" font="vector" rot="R270" xref="yes"/>
</segment>
</net>
<net name="PF0" class="0">
<segment>
<pinref part="U1" gate="G$1" pin="PF0/ADC0"/>
<wire x1="167.64" y1="17.78" x2="170.18" y2="17.78" width="0.1524" layer="91"/>
<label x="170.18" y="17.78" size="1.27" layer="95" font="vector" xref="yes"/>
</segment>
<segment>
<pinref part="CN7" gate="G$1" pin="8"/>
<wire x1="245.11" y1="120.65" x2="245.11" y2="118.11" width="0.1524" layer="91"/>
<label x="245.11" y="118.11" size="1.27" layer="95" font="vector" rot="R270" xref="yes"/>
</segment>
</net>
<net name="PD2" class="0">
<segment>
<pinref part="U1" gate="G$1" pin="PD2/RXD1/INT2"/>
<wire x1="167.64" y1="53.34" x2="170.18" y2="53.34" width="0.1524" layer="91"/>
<label x="170.18" y="53.34" size="1.27" layer="95" font="vector" xref="yes"/>
</segment>
<segment>
<pinref part="CN5" gate="G$1" pin="9"/>
<wire x1="270.51" y1="16.51" x2="270.51" y2="19.05" width="0.1524" layer="91"/>
<label x="270.51" y="19.05" size="1.27" layer="95" font="vector" rot="R90" xref="yes"/>
</segment>
</net>
<net name="PD3" class="0">
<segment>
<pinref part="U1" gate="G$1" pin="PD3/TXD1/INT3"/>
<wire x1="167.64" y1="55.88" x2="170.18" y2="55.88" width="0.1524" layer="91"/>
<label x="170.18" y="55.88" size="1.27" layer="95" font="vector" xref="yes"/>
</segment>
<segment>
<pinref part="CN5" gate="G$1" pin="10"/>
<wire x1="275.59" y1="16.51" x2="275.59" y2="19.05" width="0.1524" layer="91"/>
<label x="275.59" y="19.05" size="1.27" layer="95" font="vector" rot="R90" xref="yes"/>
</segment>
</net>
<net name="PD1" class="0">
<segment>
<pinref part="U1" gate="G$1" pin="PD1/SDA/INT1"/>
<wire x1="167.64" y1="50.8" x2="170.18" y2="50.8" width="0.1524" layer="91"/>
<label x="170.18" y="50.8" size="1.27" layer="95" font="vector" xref="yes"/>
</segment>
<segment>
<pinref part="CN5" gate="G$1" pin="8"/>
<wire x1="265.43" y1="16.51" x2="265.43" y2="19.05" width="0.1524" layer="91"/>
<label x="265.43" y="19.05" size="1.27" layer="95" font="vector" rot="R90" xref="yes"/>
</segment>
</net>
<net name="PD0" class="0">
<segment>
<pinref part="U1" gate="G$1" pin="PD0/OC0B/SCL/INT0"/>
<wire x1="167.64" y1="48.26" x2="170.18" y2="48.26" width="0.1524" layer="91"/>
<label x="170.18" y="48.26" size="1.27" layer="95" font="vector" xref="yes"/>
</segment>
<segment>
<pinref part="CN5" gate="G$1" pin="7"/>
<wire x1="260.35" y1="16.51" x2="260.35" y2="19.05" width="0.1524" layer="91"/>
<label x="260.35" y="19.05" size="1.27" layer="95" font="vector" rot="R90" xref="yes"/>
</segment>
</net>
<net name="PB7" class="0">
<segment>
<pinref part="U1" gate="G$1" pin="PB7/PCINT7/OC0A/OC1C/!RTS"/>
<wire x1="167.64" y1="96.52" x2="170.18" y2="96.52" width="0.1524" layer="91"/>
<label x="170.18" y="96.52" size="1.27" layer="95" font="vector" xref="yes"/>
</segment>
<segment>
<pinref part="CN5" gate="G$1" pin="1"/>
<wire x1="229.87" y1="16.51" x2="229.87" y2="19.05" width="0.1524" layer="91"/>
<label x="229.87" y="19.05" size="1.27" layer="95" font="vector" rot="R90" xref="yes"/>
</segment>
</net>
<net name="PB6" class="0">
<segment>
<pinref part="U1" gate="G$1" pin="PB6/PCINT6/OC1B/OC4B/ADC13"/>
<wire x1="167.64" y1="93.98" x2="170.18" y2="93.98" width="0.1524" layer="91"/>
<label x="170.18" y="93.98" size="1.27" layer="95" font="vector" xref="yes"/>
</segment>
<segment>
<pinref part="CN6" gate="G$1" pin="8"/>
<wire x1="300.99" y1="78.74" x2="298.45" y2="78.74" width="0.1524" layer="91"/>
<label x="298.45" y="78.74" size="1.27" layer="95" font="vector" rot="R180" xref="yes"/>
</segment>
</net>
<net name="PB5" class="0">
<segment>
<pinref part="U1" gate="G$1" pin="PB5/PCINT5/OC1A/!OC4B!/ADC12"/>
<wire x1="167.64" y1="91.44" x2="170.18" y2="91.44" width="0.1524" layer="91"/>
<label x="170.18" y="91.44" size="1.27" layer="95" font="vector" xref="yes"/>
</segment>
<segment>
<pinref part="CN6" gate="G$1" pin="7"/>
<wire x1="300.99" y1="73.66" x2="298.45" y2="73.66" width="0.1524" layer="91"/>
<label x="298.45" y="73.66" size="1.27" layer="95" font="vector" rot="R180" xref="yes"/>
</segment>
</net>
<net name="PB4" class="0">
<segment>
<pinref part="U1" gate="G$1" pin="PB4/PCINT4/ADC11"/>
<wire x1="167.64" y1="88.9" x2="170.18" y2="88.9" width="0.1524" layer="91"/>
<label x="170.18" y="88.9" size="1.27" layer="95" font="vector" xref="yes"/>
</segment>
<segment>
<pinref part="CN6" gate="G$1" pin="6"/>
<wire x1="300.99" y1="68.58" x2="298.45" y2="68.58" width="0.1524" layer="91"/>
<label x="298.45" y="68.58" size="1.27" layer="95" font="vector" rot="R180" xref="yes"/>
</segment>
</net>
<net name="PB3" class="0">
<segment>
<pinref part="U1" gate="G$1" pin="PB3/PDO/PCINT3/MISO"/>
<wire x1="167.64" y1="86.36" x2="170.18" y2="86.36" width="0.1524" layer="91"/>
<label x="170.18" y="86.36" size="1.27" layer="95" font="vector" xref="yes"/>
</segment>
<segment>
<pinref part="CN4" gate="G$1" pin="1"/>
<wire x1="209.55" y1="36.83" x2="212.09" y2="36.83" width="0.1524" layer="91"/>
<label x="212.09" y="36.83" size="1.27" layer="95" font="vector" xref="yes"/>
</segment>
<segment>
<pinref part="CN1" gate="G$1" pin="MISO"/>
<wire x1="10.16" y1="34.29" x2="7.62" y2="34.29" width="0.1524" layer="91"/>
<label x="7.62" y="34.29" size="1.27" layer="95" font="vector" rot="R180" xref="yes"/>
</segment>
</net>
<net name="PB2" class="0">
<segment>
<pinref part="U1" gate="G$1" pin="PB2/PDI/PCINT2/MOSI"/>
<wire x1="167.64" y1="83.82" x2="170.18" y2="83.82" width="0.1524" layer="91"/>
<label x="170.18" y="83.82" size="1.27" layer="95" font="vector" xref="yes"/>
</segment>
<segment>
<pinref part="CN4" gate="G$1" pin="2"/>
<wire x1="209.55" y1="41.91" x2="212.09" y2="41.91" width="0.1524" layer="91"/>
<label x="212.09" y="41.91" size="1.27" layer="95" font="vector" xref="yes"/>
</segment>
<segment>
<pinref part="CN1" gate="G$1" pin="MOSI"/>
<wire x1="40.64" y1="29.21" x2="43.18" y2="29.21" width="0.1524" layer="91"/>
<label x="43.18" y="29.21" size="1.27" layer="95" font="vector" xref="yes"/>
</segment>
</net>
<net name="PB1" class="0">
<segment>
<pinref part="U1" gate="G$1" pin="PB1/PCINT1/SCL"/>
<wire x1="167.64" y1="81.28" x2="170.18" y2="81.28" width="0.1524" layer="91"/>
<label x="170.18" y="81.28" size="1.27" layer="95" font="vector" xref="yes"/>
</segment>
<segment>
<pinref part="CN4" gate="G$1" pin="3"/>
<wire x1="209.55" y1="46.99" x2="212.09" y2="46.99" width="0.1524" layer="91"/>
<label x="212.09" y="46.99" size="1.27" layer="95" font="vector" xref="yes"/>
</segment>
<segment>
<pinref part="CN1" gate="G$1" pin="SCK"/>
<wire x1="10.16" y1="29.21" x2="7.62" y2="29.21" width="0.1524" layer="91"/>
<label x="7.62" y="29.21" size="1.27" layer="95" font="vector" rot="R180" xref="yes"/>
</segment>
</net>
<net name="PB0" class="0">
<segment>
<pinref part="U1" gate="G$1" pin="PB0/SS/PCINT0"/>
<wire x1="167.64" y1="78.74" x2="170.18" y2="78.74" width="0.1524" layer="91"/>
<label x="170.18" y="78.74" size="1.27" layer="95" font="vector" xref="yes"/>
</segment>
<segment>
<pinref part="CN4" gate="G$1" pin="4"/>
<wire x1="209.55" y1="52.07" x2="212.09" y2="52.07" width="0.1524" layer="91"/>
<label x="212.09" y="52.07" size="1.27" layer="95" font="vector" xref="yes"/>
</segment>
</net>
<net name="PC7" class="0">
<segment>
<pinref part="U1" gate="G$1" pin="PC7/ICP3/CLK0/OC4A"/>
<wire x1="167.64" y1="73.66" x2="170.18" y2="73.66" width="0.1524" layer="91"/>
<label x="170.18" y="73.66" size="1.27" layer="95" font="vector" xref="yes"/>
</segment>
<segment>
<pinref part="R9" gate="G$1" pin="P$2"/>
<wire x1="322.58" y1="93.98" x2="322.58" y2="100.33" width="0.1524" layer="91"/>
<wire x1="322.58" y1="100.33" x2="299.72" y2="100.33" width="0.1524" layer="91"/>
<pinref part="CN6" gate="G$1" pin="10"/>
<wire x1="300.99" y1="88.9" x2="299.72" y2="88.9" width="0.1524" layer="91"/>
<label x="298.45" y="88.9" size="1.27" layer="95" font="vector" rot="R180" xref="yes"/>
<wire x1="299.72" y1="88.9" x2="298.45" y2="88.9" width="0.1524" layer="91"/>
<wire x1="299.72" y1="100.33" x2="299.72" y2="88.9" width="0.1524" layer="91"/>
<junction x="299.72" y="88.9"/>
</segment>
</net>
<net name="PC6" class="0">
<segment>
<pinref part="U1" gate="G$1" pin="PC6/OC3A/!OC4A"/>
<wire x1="167.64" y1="71.12" x2="170.18" y2="71.12" width="0.1524" layer="91"/>
<label x="170.18" y="71.12" size="1.27" layer="95" font="vector" xref="yes"/>
</segment>
<segment>
<pinref part="CN6" gate="G$1" pin="9"/>
<wire x1="300.99" y1="83.82" x2="298.45" y2="83.82" width="0.1524" layer="91"/>
<label x="298.45" y="83.82" size="1.27" layer="95" font="vector" rot="R180" xref="yes"/>
</segment>
</net>
<net name="PD7" class="0">
<segment>
<pinref part="U1" gate="G$1" pin="PD7/T0/OC4D/ADC10"/>
<wire x1="167.64" y1="66.04" x2="170.18" y2="66.04" width="0.1524" layer="91"/>
<label x="170.18" y="66.04" size="1.27" layer="95" font="vector" xref="yes"/>
</segment>
<segment>
<pinref part="CN6" gate="G$1" pin="5"/>
<wire x1="300.99" y1="63.5" x2="298.45" y2="63.5" width="0.1524" layer="91"/>
<label x="298.45" y="63.5" size="1.27" layer="95" font="vector" rot="R180" xref="yes"/>
</segment>
</net>
<net name="PD6" class="0">
<segment>
<pinref part="U1" gate="G$1" pin="PD6/T1/!OC4D!/ADC9"/>
<wire x1="167.64" y1="63.5" x2="170.18" y2="63.5" width="0.1524" layer="91"/>
<label x="170.18" y="63.5" size="1.27" layer="95" font="vector" xref="yes"/>
</segment>
<segment>
<pinref part="CN6" gate="G$1" pin="4"/>
<wire x1="300.99" y1="58.42" x2="298.45" y2="58.42" width="0.1524" layer="91"/>
<label x="298.45" y="58.42" size="1.27" layer="95" font="vector" rot="R180" xref="yes"/>
</segment>
</net>
<net name="PD5" class="0">
<segment>
<pinref part="U1" gate="G$1" pin="PD5/XCK1/!CTS"/>
<wire x1="167.64" y1="60.96" x2="170.18" y2="60.96" width="0.1524" layer="91"/>
<label x="170.18" y="60.96" size="1.27" layer="95" font="vector" xref="yes"/>
</segment>
<segment>
<pinref part="CN5" gate="G$1" pin="11"/>
<wire x1="280.67" y1="16.51" x2="280.67" y2="19.05" width="0.1524" layer="91"/>
<label x="280.67" y="19.05" size="1.27" layer="95" font="vector" rot="R90" xref="yes"/>
</segment>
</net>
<net name="PD4" class="0">
<segment>
<pinref part="U1" gate="G$1" pin="PD4/ICP1/ADC8"/>
<wire x1="167.64" y1="58.42" x2="170.18" y2="58.42" width="0.1524" layer="91"/>
<label x="170.18" y="58.42" size="1.27" layer="95" font="vector" xref="yes"/>
</segment>
<segment>
<pinref part="CN6" gate="G$1" pin="3"/>
<wire x1="300.99" y1="53.34" x2="298.45" y2="53.34" width="0.1524" layer="91"/>
<label x="298.45" y="53.34" size="1.27" layer="95" font="vector" rot="R180" xref="yes"/>
</segment>
</net>
<net name="PE6" class="0">
<segment>
<pinref part="U1" gate="G$1" pin="PE6/INT6/AIN0"/>
<wire x1="167.64" y1="43.18" x2="170.18" y2="43.18" width="0.1524" layer="91"/>
<label x="170.18" y="43.18" size="1.27" layer="95" font="vector" xref="yes"/>
</segment>
<segment>
<pinref part="CN3" gate="G$1" pin="6"/>
<wire x1="209.55" y1="100.33" x2="212.09" y2="100.33" width="0.1524" layer="91"/>
<label x="212.09" y="100.33" size="1.27" layer="95" font="vector" xref="yes"/>
</segment>
</net>
<net name="PE2" class="0">
<segment>
<pinref part="CN6" gate="G$1" pin="11"/>
<wire x1="300.99" y1="93.98" x2="298.45" y2="93.98" width="0.1524" layer="91"/>
<label x="298.45" y="93.98" size="1.27" layer="95" font="vector" rot="R180" xref="yes"/>
</segment>
<segment>
<pinref part="R2" gate="G$1" pin="P$2"/>
<pinref part="U1" gate="G$1" pin="PE2/!HWB"/>
<wire x1="179.07" y1="34.29" x2="179.07" y2="40.64" width="0.1524" layer="91"/>
<wire x1="179.07" y1="40.64" x2="167.64" y2="40.64" width="0.1524" layer="91"/>
<label x="181.61" y="40.64" size="1.27" layer="95" font="vector" xref="yes"/>
<wire x1="181.61" y1="40.64" x2="179.07" y2="40.64" width="0.1524" layer="91"/>
<junction x="179.07" y="40.64"/>
</segment>
</net>
<net name="N$2" class="0">
<segment>
<pinref part="R9" gate="G$1" pin="P$1"/>
<pinref part="D3" gate="G$1" pin="A"/>
<wire x1="322.58" y1="87.63" x2="322.58" y2="86.36" width="0.1524" layer="91"/>
</segment>
</net>
</nets>
</sheet>
</sheets>
</schematic>
</drawing>
<compatibility>
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
