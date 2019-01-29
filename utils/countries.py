# -*- coding: utf-8 -*-
# Copyright 2008-2016 by Carnegie Mellon University
# See license information in LICENSE-OPENSOURCE.txt

"""
Definitions of country and region names and codes as defined by ISO
3166-1 and the UN Statistics Division.  The information in this module
is current as of September 2015.
"""

# ISO-3166-1 alpha-2, alpha-3, and numeric codes are from Wikipedia:
#   https://en.wikipedia.org/wiki/ISO_3166-1
# The list at the bottom contains English short name, alpha-2,
# alpha-3, and numeric codes)
#
# The sub-regions and regions are from
#   http://unstats.un.org/unsd/methods/m49/m49alpha.htm
#
# ccTLDs are from IANA, via
#   https://en.wikipedia.org/wiki/List_of_Internet_top-level_domains#Country_code_top-level_domains
#
# It might also be useful to add STANAG 1059 three-letter codes (used
# by NATO) to this. These are mostly but not entirely the same as
# ISO-3166-1 alpha-3 codes.


### | CC | CCC | Name                                        | Sub | Reg | TLDs
_country_info = """

# Source Notes:
#   !UNS: United Nations Statistics Division does not use this entry
#   UNS: UNSD uses this entry, but it does not exist in ISO-3166-1
#   A2-ER: ISO-3166-1 alpha-2 exceptional reservation
#   A3-ER: ISO-3166-1 alpha-3 exceptional reservation
#   A2-TR: ISO-3166-1 alpha-2 transitional reservation
#   A3-TR: ISO-3166-1 alpha-3 transitional reservation
#   IANA: IANA has a country code for this entry, but it doesn't exist in ISO-3166-1
#   IANA-R: IANA has a retired entry for this

# Entries which are in ISO-3166-1 (according to Wikipedia)

004 | AF | AFG | Afghanistan                                 | 034 | 142 | af
248 | AX | ALA | Åland Islands                               | 154 | 150 | ax
008 | AL | ALB | Albania                                     | 039 | 150 | al
012 | DZ | DZA | Algeria                                     | 015 | 002 | dz
016 | AS | ASM | American Samoa                              | 061 | 009 | as
020 | AD | AND | Andorra                                     | 039 | 150 | ad
024 | AO | AGO | Angola                                      | 017 | 002 | ao
660 | AI | AIA | Anguilla                                    | 029 | 019 | ai
010 | AQ | ATA | Antarctica                                  |     | 990 | aq # !UNS
028 | AG | ATG | Antigua and Barbuda                         | 029 | 019 | ag
032 | AR | ARG | Argentina                                   | 005 | 019 | ar
051 | AM | ARM | Armenia                                     | 145 | 142 | am
533 | AW | ABW | Aruba                                       | 029 | 019 | aw
036 | AU | AUS | Australia                                   | 053 | 009 | au
040 | AT | AUT | Austria                                     | 155 | 150 | at
031 | AZ | AZE | Azerbaijan                                  | 145 | 142 | az
044 | BS | BHS | Bahamas                                     | 029 | 019 | bs
048 | BH | BHR | Bahrain                                     | 145 | 142 | bh
050 | BD | BGD | Bangladesh                                  | 034 | 142 | bd
052 | BB | BRB | Barbados                                    | 029 | 019 | bb
112 | BY | BLR | Belarus                                     | 151 | 150 | by
056 | BE | BEL | Belgium                                     | 155 | 150 | be
084 | BZ | BLZ | Belize                                      | 013 | 019 | bz
204 | BJ | BEN | Benin                                       | 011 | 002 | bj
060 | BM | BMU | Bermuda                                     | 021 | 019 | bm
064 | BT | BTN | Bhutan                                      | 034 | 142 | bt
068 | BO | BOL | Bolivia (Plurinational State of)            | 005 | 019 | bo
535 | BQ | BES | Bonaire, Sint Eustatius and Saba            | 029 | 019 | bq
070 | BA | BIH | Bosnia and Herzegovina                      | 039 | 150 | ba
072 | BW | BWA | Botswana                                    | 018 | 002 | bw
074 | BV | BVT | Bouvet Island                               |     | 990 | bv # !UNS
076 | BR | BRA | Brazil                                      | 005 | 019 | br
086 | IO | IOT | British Indian Ocean Territory              |     | 990 | io # !UNS
096 | BN | BRN | Brunei Darussalam                           | 035 | 142 | bn
100 | BG | BGR | Bulgaria                                    | 151 | 150 | bg
854 | BF | BFA | Burkina Faso                                | 011 | 002 | bf
108 | BI | BDI | Burundi                                     | 014 | 002 | bi
132 | CV | CPV | Cabo Verde                                  | 011 | 002 | cv
116 | KH | KHM | Cambodia                                    | 035 | 142 | kh
120 | CM | CMR | Cameroon                                    | 017 | 002 | cm
124 | CA | CAN | Canada                                      | 021 | 019 | ca
136 | KY | CYM | Cayman Islands                              | 029 | 019 | ky
140 | CF | CAF | Central African Republic                    | 017 | 002 | cf
148 | TD | TCD | Chad                                        | 017 | 002 | td
152 | CL | CHL | Chile                                       | 005 | 019 | cl
156 | CN | CHN | China                                       | 030 | 142 | cn
162 | CX | CXR | Christmas Island                            |     | 990 | cx # !UNS
166 | CC | CCK | Cocos (Keeling) Islands                     |     | 990 | cc # !UNS
170 | CO | COL | Colombia                                    | 005 | 019 | co
174 | KM | COM | Comoros                                     | 014 | 002 | km
178 | CG | COG | Congo                                       | 017 | 002 | cg
180 | CD | COD | Congo (Democratic Republic of the)          | 017 | 002 | cd
184 | CK | COK | Cook Islands                                | 061 | 009 | ck
188 | CR | CRI | Costa Rica                                  | 013 | 019 | cr
384 | CI | CIV | Côte d'Ivoire                               | 011 | 002 | ci
191 | HR | HRV | Croatia                                     | 039 | 150 | hr
192 | CU | CUB | Cuba                                        | 029 | 019 | cu
531 | CW | CUW | Curaçao                                     | 029 | 019 | cw
196 | CY | CYP | Cyprus                                      | 145 | 142 | cy
203 | CZ | CZE | Czech Republic                              | 151 | 150 | cz
208 | DK | DNK | Denmark                                     | 154 | 150 | dk
262 | DJ | DJI | Djibouti                                    | 014 | 002 | dj
212 | DM | CMA | Dominica                                    | 029 | 019 | dm
214 | DO | DOM | Dominican Republic                          | 029 | 019 | do
218 | EC | ECU | Ecuador                                     | 005 | 019 | ec
818 | EG | EGY | Egypt                                       | 015 | 002 | eg
222 | SV | SLV | El Salvador                                 | 013 | 019 | sv
226 | GQ | GNQ | Equatorial Guinea                           | 017 | 002 | gq
232 | ER | ERI | Eritrea                                     | 014 | 002 | er
233 | EE | EST | Estonia                                     | 154 | 150 | ee
231 | ET | ETH | Ethiopia                                    | 014 | 002 | et
238 | FK | FLK | Falkland Islands (Malvinas)                 | 005 | 019 | fk
234 | FO | FRO | Faroe Islands                               | 154 | 150 | fo
242 | FJ | FJI | Fiji                                        | 054 | 009 | fj
246 | FI | FIN | Finland                                     | 154 | 150 | fi
250 | FR | FRA | France                                      | 155 | 150 | fr
254 | GF | GUF | French Guiana                               | 005 | 019 | gf
258 | PF | PYF | French Polynesia                            | 061 | 009 | pf
260 | TF | ATF | French Southern Territories                 |     | 990 | tf # !UNS
266 | GA | GAB | Gabon                                       | 017 | 002 | ga
270 | GM | GMB | Gambia                                      | 011 | 002 | gm
268 | GE | GEO | Georgia                                     | 145 | 142 | ge
276 | DE | DEU | Germany                                     | 155 | 150 | de
288 | GH | GHA | Ghana                                       | 011 | 002 | gh
292 | GI | GIB | Gibraltar                                   | 039 | 150 | gi
300 | GR | GRC | Greece                                      | 039 | 150 | gr
304 | GL | GRL | Greenland                                   | 021 | 019 | gl
308 | GD | GRD | Grenada                                     | 029 | 019 | gd
312 | GP | GLP | Guadeloupe                                  | 029 | 019 | gp
316 | GU | GUM | Guam                                        | 057 | 009 | gu
320 | GT | GTM | Guatemala                                   | 013 | 019 | gt
831 | GG | GGY | Guernsey                                    | 154 | 150 | gg
324 | GN | GIN | Guinea                                      | 011 | 002 | gn
624 | GW | GNB | Guinea-Bissau                               | 011 | 002 | gw
328 | GY | GUY | Guyana                                      | 005 | 019 | gy
332 | HT | HTI | Haiti                                       | 029 | 019 | ht
334 | HM | HMD | Heard Island and Mcdonald Islands           |     | 990 | hm # !UNS
336 | VA | VAT | Holy See                                    | 039 | 150 | va
340 | HN | HND | Honduras                                    | 013 | 019 | hn
344 | HK | HKG | Hong Kong                                   | 030 | 142 | hk
348 | HU | HUN | Hungary                                     | 151 | 150 | hu
352 | IS | ISL | Iceland                                     | 154 | 150 | is
356 | IN | IND | India                                       | 034 | 142 | in
360 | ID | IDN | Indonesia                                   | 035 | 142 | id
364 | IR | IRN | Iran (Islamic Republic of)                  | 034 | 142 | ir
368 | IQ | IRQ | Iraq                                        | 145 | 142 | iq
372 | IE | IRL | Ireland                                     | 154 | 150 | ie
833 | IM | IMN | Isle of Man                                 | 154 | 150 | im
376 | IL | ISR | Israel                                      | 145 | 142 | il
380 | IT | ITA | Italy                                       | 039 | 150 | it
388 | JM | JAM | Jamaica                                     | 029 | 019 | jm
392 | JP | JPN | Japan                                       | 030 | 142 | jp
832 | JE | JEY | Jersey                                      | 154 | 150 | je
400 | JO | JOR | Jordan                                      | 145 | 142 | jo
398 | KZ | KAZ | Kazakhstan                                  | 143 | 142 | kz
404 | KE | KEN | Kenya                                       | 014 | 002 | ke
296 | KI | KIR | Kiribati                                    | 057 | 009 | ki
408 | KP | PRK | Korea (Democratic People's Republic of)     | 030 | 142 | kp
410 | KR | KOR | Korea (Republic of)                         | 030 | 142 | kr
414 | KW | KWT | Kuwait                                      | 145 | 142 | kw
417 | KG | KGZ | Kyrgyzstan                                  | 143 | 142 | kg
418 | LA | LAO | Lao People's Democratic Republic            | 035 | 142 | la
428 | LV | LVA | Latvia                                      | 154 | 150 | lv
422 | LB | LBN | Lebanon                                     | 145 | 142 | lb
426 | LS | LSO | Lesotho                                     | 018 | 002 | ls
430 | LR | LBR | Liberia                                     | 011 | 002 | lr
434 | LY | LBY | Libya                                       | 015 | 002 | ly
438 | LI | LIE | Liechtenstein                               | 155 | 150 | li
440 | LT | LTU | Lithuania                                   | 154 | 150 | lt
442 | LU | LUX | Luxembourg                                  | 155 | 150 | lu
446 | MO | MAC | Macao                                       | 030 | 142 | mo
807 | MK | MKD | Macedonia (the Former Yugoslav Republic of) | 039 | 150 | mk
450 | MG | MDG | Madagascar                                  | 014 | 002 | mg
454 | MW | MWI | Malawi                                      | 014 | 002 | mw
458 | MY | MYS | Malaysia                                    | 035 | 142 | my
462 | MV | MDV | Maldives                                    | 034 | 142 | mv
466 | ML | MLI | Mali                                        | 011 | 002 | ml
470 | MT | MLT | Malta                                       | 039 | 150 | mt
584 | MH | MHL | Marshall Islands                            | 057 | 009 | mh
474 | MQ | MTQ | Martinique                                  | 029 | 019 | mq
478 | MR | MRT | Mauritania                                  | 011 | 002 | mr
480 | MU | MUS | Mauritius                                   | 014 | 002 | mu
175 | YT | MYT | Mayotte                                     | 014 | 002 | yt
484 | MX | MEX | Mexico                                      | 013 | 019 | mx
583 | FM | FSM | Micronesia (Federated States of)            | 057 | 009 | fm
498 | MD | MDA | Moldova (Republic of)                       | 151 | 150 | md
492 | MC | MCO | Monaco                                      | 155 | 150 | mc
496 | MN | MNG | Mongolia                                    | 030 | 142 | mn
499 | ME | MNE | Montenegro                                  | 039 | 150 | me
500 | MS | MSR | Montserrat                                  | 029 | 019 | ms
504 | MA | MAR | Morocco                                     | 015 | 002 | ma
508 | MZ | MOZ | Mozambique                                  | 014 | 002 | mz
104 | MM | MMR | Myanmar                                     | 035 | 142 | mm
516 | NA | NAM | Namibia                                     | 018 | 002 | na
520 | NR | NRU | Nauru                                       | 057 | 009 | nr
524 | NP | NPL | Nepal                                       | 034 | 142 | np
528 | NL | NLD | Netherlands                                 | 155 | 150 | nl
540 | NC | NCL | New Caledonia                               | 054 | 009 | nc
554 | NZ | NZL | New Zealand                                 | 053 | 009 | nz
558 | NI | NIC | Nicaragua                                   | 013 | 019 | ni
562 | NE | NER | Niger                                       | 011 | 002 | ne
566 | NG | NGA | Nigeria                                     | 011 | 002 | ng
570 | NU | NIU | Niue                                        | 061 | 009 | nu
574 | NF | NFK | Norfolk Island                              | 053 | 009 | nf
580 | MP | MNP | Northern Mariana Islands                    | 057 | 009 | mp
578 | NO | NOR | Norway                                      | 154 | 150 | no
512 | OM | OMN | Oman                                        | 145 | 142 | om
586 | PK | PAK | Pakistan                                    | 034 | 142 | pk
585 | PW | PLW | Palau                                       | 057 | 009 | pw
275 | PS | PSE | Palestine, State of                         | 145 | 142 | ps
591 | PA | PAN | Panama                                      | 013 | 019 | pa
598 | PG | PNG | Papua New Guinea                            | 054 | 009 | pg
600 | PY | PRY | Paraguay                                    | 005 | 019 | py
604 | PE | PER | Peru                                        | 005 | 019 | pe
608 | PH | PHL | Philippines                                 | 035 | 142 | ph
612 | PN | PCN | Pitcairn                                    | 061 | 009 | pn
616 | PL | POL | Poland                                      | 151 | 150 | pl
620 | PT | PRT | Portugal                                    | 039 | 150 | pt
630 | PR | PRI | Puerto Rico                                 | 029 | 019 | pr
634 | QA | QAT | Qatar                                       | 145 | 142 | qa
638 | RE | REU | Réunion                                     | 014 | 002 | re
642 | RO | ROU | Romania                                     | 151 | 150 | ro
643 | RU | RUS | Russian Federation                          | 151 | 150 | ru
646 | RW | RWA | Rwanda                                      | 014 | 002 | rw
652 | BL | BLM | Saint Barthélemy                            | 029 | 019 | bl
654 | SH | SHN | Saint Helena, Ascension and Tristan da Cunha| 011 | 002 | sh
659 | KN | KNA | Saint Kitts and Nevis                       | 029 | 019 | kn
662 | LC | LCA | Saint Lucia                                 | 029 | 019 | lc
663 | MF | MAF | Saint Martin (French part)                  | 029 | 019 | mf
666 | PM | SPM | Saint Pierre and Miquelon                   | 021 | 019 | pm
670 | VC | VCT | Saint Vincent and the Grenadines            | 029 | 019 | vc
882 | WS | WSM | Samoa                                       | 061 | 009 | ws
674 | SM | SMR | San Marino                                  | 039 | 150 | sm
678 | ST | STP | Sao Tome and Principe                       | 017 | 002 | st
682 | SA | SAU | Saudi Arabia                                | 145 | 142 | sa
686 | SN | SEN | Senegal                                     | 011 | 002 | sn
688 | RS | SRB | Serbia                                      | 039 | 150 | rs
690 | SC | SYC | Seychelles                                  | 014 | 002 | sc
694 | SL | SLE | Sierra Leone                                | 011 | 002 | sl
702 | SG | SGP | Singapore                                   | 035 | 142 | sg
534 | SX | SXM | Sint Maarten (Dutch part)                   | 029 | 019 | sx
703 | SK | SVK | Slovakia                                    | 151 | 150 | sk
705 | SI | SVN | Slovenia                                    | 039 | 150 | si
090 | SB | SLB | Solomon Islands                             | 054 | 009 | sb
706 | SO | SOM | Somalia                                     | 014 | 002 | so
710 | ZA | ZAF | South Africa                                | 018 | 002 | za
239 | GS | SGS | South Georgia and the South Sandwich Islands|     | 990 | gs # !UNS
728 | SS | SSD | South Sudan                                 | 014 | 002 | ss
724 | ES | ESP | Spain                                       | 039 | 150 | es
144 | LK | LKA | Sri Lanka                                   | 034 | 142 | lk
729 | SD | SDN | Sudan                                       | 015 | 002 | sd
740 | SR | SUR | Suriname                                    | 005 | 019 | sr
744 | SJ | SJM | Svalbard and Jan Mayen                      | 154 | 150 | sj
748 | SZ | SWZ | Swaziland                                   | 018 | 002 | sz
752 | SE | SWE | Sweden                                      | 154 | 150 | se
756 | CH | CHE | Switzerland                                 | 155 | 150 | ch
760 | SY | SYR | Syrian Arab Republic                        | 145 | 142 | sy
158 | TW | TWN | Taiwan, Province of China                   | 030 | 142 | tw
762 | TJ | TJK | Tajikistan                                  | 143 | 142 | tj
834 | TZ | TZA | Tanzania, United Republic of                | 014 | 002 | tz
764 | TH | THA | Thailand                                    | 035 | 142 | th
626 | TL | TLS | Timor-Leste                                 | 035 | 142 | tl
768 | TG | TGO | Togo                                        | 011 | 002 | tg
772 | TK | TKL | Tokelau                                     | 061 | 009 | tk
776 | TO | TON | Tonga                                       | 061 | 009 | to
780 | TT | TTO | Trinidad and Tobago                         | 029 | 019 | tt
788 | TN | TUN | Tunisia                                     | 015 | 002 | tn
792 | TR | TUR | Turkey                                      | 145 | 142 | tr
795 | TM | TKM | Turkmenistan                                | 143 | 142 | tm
796 | TC | TCA | Turks and Caicos Islands                    | 029 | 019 | tc
798 | TV | TUV | Tuvalu                                      | 061 | 009 | tv
800 | UG | UGA | Uganda                                      | 014 | 002 | ug
804 | UA | UKR | Ukraine                                     | 151 | 150 | ua
784 | AE | ARE | United Arab Emirates                        | 145 | 142 | ae
826 | GB | GBR | United Kingdom of Great Britain and Northern Ireland | 154 | 150 | uk gb
581 | UM | UMI | United States Minor Outlying Islands        |     | 990 | um # !UNS
840 | US | USA | United States of America                    | 021 | 019 | us
858 | UY | URY | Uruguay                                     | 005 | 019 | uy
860 | UZ | UZB | Uzbekistan                                  | 143 | 142 | uz
548 | VU | VUT | Vanuatu                                     | 054 | 009 | vu
862 | VE | VEN | Venezuela (Bolivarian Republic of)          | 005 | 019 | ve
704 | VN | VNM | Viet Nam                                    | 035 | 142 | vn
092 | VG | VGB | Virgin Islands (British)                    | 029 | 019 | vg
850 | VI | VIR | Virgin Islands (U.S.)                       | 029 | 019 | vi
876 | WF | WLF | Wallis and Futuna                           | 061 | 009 | wf
732 | EH | ESH | Western Sahara                              | 015 | 002 | eh
887 | YE | YEM | Yemen                                       | 145 | 142 | ye
894 | ZM | ZMB | Zambia                                      | 014 | 002 | zm
716 | ZW | ZWE | Zimbabwe                                    | 014 | 002 | zw

# Reserved entries from ISO-3166-1 data.

900 | AC | ASC | Ascension Island                            |     | 990 | ac # A2-ER,A3-ER,IANA
901 | CP | CPT | Clipperton Island                           |     | 990 |    # A2-ER,A3-ER
902 | DG | DGA | Diego Garcia                                |     | 990 |    # A2-ER,A3-ER
903 | EA |     | Ceuta, Melilla                              |     | 990 |    # A2-ER
904 | EU |     | European Union                              |     | 990 | eu # A2-ER,IANA
905 | EZ |     | Eurozone                                    |     | 990 |    # A2-ER
906 | FX | FXX | France, Metropolitan                        |     | 990 |    # A2-ER,A3-ER
907 | IC |     | Canary Islands                              |     | 990 |    # A2-ER
908 | SU | SUN | Union of Soviet Socialist Republics         |     | 990 | su # A2-ER,A3-ER,IANA
909 | TA | TAA | Tristan da Cunha                            |     | 990 |    # A2-ER,A3-ER
#910| UK |     | United Kingdom                              |     | 990 |    # A2-ER
#This entry is a clusterfuck because of the UK/GB thing
911 | UN |     | United Nations                              |     | 990 |    # A2-ER

912 | AN | ANT | Netherlands Antilles                        |     | 990 | an # A2-TR,IANA-R
913 | BU | BUR | Burma                                       |     | 990 |    # A2-TR
914 |    | BYS | Byelorussian SSR                            |     | 990 |    # A3-TR
915 | CS | SCG | Serbia and Montenegro                       |     | 990 |    # A2-TR
916 |    | CSK | Czechoslovakia                              |     | 990 |    # A3-TR
917 | NT | NTZ | Neutral Zone                                |     | 990 |    # A2-TR
918 |    | ROM | Romania                                     |     | 990 |    # A3-TR
919 | SF |     | Finland                                     |     | 990 |    # A2-TR
920 |    | TMP | East Timor                                  |     | 990 | tp # A2-TR,IANA-R
921 | YU | YUG | Yugoslavia                                  |     | 990 |    # A2-TR
922 | ZR | ZAR | Zaire                                       |     | 990 |    # A2-TR

# Entries in UN Statistics Division data, but not ISO-3166-1

830 |    |     | Channel Islands                             | 154 | 150 |    # UNS
680 |    |     | Sark                                        | 154 | 150 |    # UNS

# Private use entries

991 | QM | QMZ | Anonymous Proxies                           |     | 990 | a1
992 | QN | QNZ | Satellite Providers                         |     | 990 | a2
999 | ZZ | ZZZ | Unknown                                     |     | 990 | --
"""

### | Name                      | Subregions          | Superregion
_region_info = """
002 | Africa                    | 015 014 017 018 011 |
015 | Northern Africa           |                     | 002
014 | Eastern Africa            |                     | 002
017 | Middle Africa             |                     | 002
018 | Southern Africa           |                     | 002
011 | Western Africa            |                     | 002
019 | Americas                  | 029 013 005 021     |
029 | Caribbean                 |                     | 019
013 | Central America           |                     | 019
005 | South America             |                     | 019
021 | Northern America          |                     | 019
142 | Asia                      | 143 030 034 035 145 |
143 | Central Asia              |                     | 142
030 | Eastern Asia              |                     | 142
034 | Southern Asia             |                     | 142
035 | South-Eastern Asia        |                     | 142
145 | Western Asia              |                     | 142
150 | Europe                    | 151 154 039 155     |
151 | Eastern Europe            |                     | 150
154 | Northern Europe           |                     | 150
039 | Southern Europe           |                     | 150
155 | Western Europe            |                     | 150
009 | Oceania                   | 053 054 057 061     |
053 | Australia and New Zealand |                     | 009
054 | Melanesia                 |                     | 009
057 | Micronesia                |                     | 009
061 | Polynesia                 |                     | 009
990 | Other                     |                     |
"""

_area_name = {}                 # Numeric ID to name
_area_tlds = {}                 # Numeric ID to list of TLDs

_country_alpha2 = {}            # Numeric ID to alpha-2 or None
_country_alpha3 = {}            # Numeric ID to alpha-3 or None
_country_region = {}            # Numeric ID to region's numeric ID
_country_subregion = {}         # Numeric ID to subregion's numeric ID
_country_lookup = {}            # Name to numeric ID

_region_countries = {}          # List for each region of countries
_region_subregions = {}         # List for each region of subregions
_region_superregion = {}        # ID of superregion or None for each region

_country_list = []              # List of numeric IDs for actual countries
_region_list = []               # List of numeric IDs for regions

# Parse country data from giant text blob
for line in _country_info.split("\n"):
    if '#' in line: line = line[:line.index('#')]
    line = line.strip()
    if not line: continue
    if line.startswith('#'): continue
    (num, alpha2, alpha3, name, subregion, region, tlds) = [
        column.strip() for column in line.split("|")]
    tlds = [tld.strip() for tld in tlds.split()]
    num = int(num)
    if not alpha2: alpha2 = None
    if not alpha3: alpha3 = None
    _country_list.append(num)
    if subregion:
        subregion = int(subregion)
        if subregion not in _region_countries:
            _region_countries[subregion] = []
        _region_countries[subregion].append(num)
        _country_subregion[num] = subregion
    else:
        subregion = None
    if region:
        region = int(region)
        if region not in _region_countries:
            _region_countries[region] = []
        _region_countries[region].append(num)
        _country_region[num] = region
        if region == 990:       # "Other" special case
            _country_subregion[num] = region
    else:
        region = None
    _area_name[num] = name
    lookup_names = []
    _country_alpha2[num] = alpha2
    if alpha2:
        lookup_names.append(alpha2)
    _country_alpha3[num] = alpha3
    if alpha3:
        lookup_names.append(alpha3)
    if tlds:
        update_lists = [lookup_names]
        if num not in _area_tlds:
            _area_tlds[num] = []
        update_lists.append(_area_tlds[num])
        if region is not None:
            if region not in _area_tlds:
                _area_tlds[region] = []
            update_lists.append(_area_tlds[region])
        if subregion is not None:
            if subregion not in _area_tlds:
                _area_tlds[subregion] = []
            update_lists.append(_area_tlds[subregion])
        for tld in tlds:
            for update_list in update_lists:
                update_list.append(tld)
    for lookup_name in lookup_names:
        _country_lookup[lookup_name.upper()] = num

# Clear out giant text blob
_country_info = None

# Parse region data from giant text blob
for line in _region_info.split("\n"):
    line = line.strip()
    if not line: continue
    (num, name, subregions, superregion) = [
        column.strip() for column in line.split("|")]
    num = int(num)
    _region_list.append(num)
    subregions = [int(x) for x in subregions.split()]
    if superregion:
        superregion = int(superregion)
    else:
        superregion = None
    _area_name[num] = name
    _region_subregions[num] = subregions
    _region_superregion[num] = superregion

# Clear out giant text blob
_region_info = None

def get_area_numeric(code):
    """
    Given a country or region code as one of the following:

        * String containing ISO 3166-1 alpha-2 code
        * String containing ISO 3166-1 alpha-3 code
        * String or integer containing ISO 3166-1 numeric code
        * String containing DNS top-level domain alpha-2 code
        * String or integer containing UN Statistics Division numeric region code

    Returns the appropriate ISO 3166-1 or UN Statistics Division
    numeric code as an integer.

    Note that some regions and other special items that are not
    defined by ISO 3166-1 or the UN Statistics Division are encoded as
    ISO 3166-1 user-assigned code elements.

    Raises :exc:`KeyError` if the code is unrecognized.
    """
    v = code
    if isinstance(v, int):
        if v in _area_name:
            return v
    elif isinstance(v, str):
        v = v.upper()
        if v in _country_lookup:
            return _country_lookup[v]
        try:
            v = int(v)
            if v in _area_name:
                return v
        except:
            pass
    raise KeyError("Unknown country or region ID %s" % repr(code))

def get_area_name(code):
    """
    Given a country or region code as a string or integer, returns the
    name for the country or region.

    Raises :exc:`KeyError` if the country or region code is unrecognized.
    """
    return _area_name[get_area_numeric(code)]

def get_area_tlds(code):
    """
    Given a country or region code as a string or integer, returns a
    list of zero or more DNS top-level domains for that country or
    region.

    Raises :exc:`KeyError` if the country or region code is unrecognized.
    """
    return _area_tlds.get(get_area_numeric(code), [])

def get_country_numeric(code):
    """
    Given a country code as a string or integer, returns the ISO
    3166-1 numeric code for the country.

    Raises :exc:`KeyError` if the country code is unrecognized.
    """
    v = code
    if isinstance(v, int):
        if v in _country_alpha2:
            return v
    elif isinstance(v, str):
        v = v.upper()
        if v in _country_lookup:
            return _country_lookup[v]
        try:
            v = int(v)
            if v in _country_alpha2:
                return v
        except:
            pass
    raise KeyError("Unknown country ID %s" % repr(code))

def get_country_name(code):
    """
    Given a country code as a string or integer, returns the name for
    the country.

    Raises :exc:`KeyError` if the country code is unrecognized.
    """
    return _area_name[get_country_numeric(code)]

def get_country_alpha2(code):
    """
    Given a country code as a string or integer, returns the ISO
    3166-1 alpha-2 code for the country, or ``None`` if that is not
    possible.

    Raises :exc:`KeyError` if the country code is unrecognized.
    """
    return _country_alpha2.get(get_country_numeric(code), None)

def get_country_alpha3(code):
    """
    Given a country code as a string or integer, returns the ISO
    3166-1 alpha-3 code for the country, or ``None`` if that is not
    possible.

    Raises :exc:`KeyError` if the country code is unrecognized.
    """
    return _country_alpha3.get(get_country_numeric(code), None)

def get_country_tlds(code):
    """
    Given a country code as a string or integer, returns a list of
    zero or more DNS top-level domains for that country.

    Raises :exc:`KeyError` if the country code is unrecognized.
    """
    return _area_tlds.get(get_country_numeric(code), [])

def get_country_region(code):
    """
    Given a country code as a string or integer, returns the numeric
    code of the top-level UN Statistics Division region that country
    belongs to as an integer. (See also `iter_regions`.)

    Raises :exc:`KeyError` if the country code is unrecognized.
    """
    return _country_region.get(get_country_numeric(code), None)

def get_country_subregion(code):
    """
    Given a country code as a string or integer, returns the numeric
    code of the lowest-level UN Statistics Division region that
    country belongs to as an integer.

    Raises :exc:`KeyError` if the country code is unrecognized.
    """
    return _country_subregion.get(get_country_numeric(code), None)

def iter_countries():

    """
    Returns an iterator which yields all known ISO 3166-1 numeric
    country codes as integers, including user-assigned code elements
    in use.
    """
    for code in _country_list:
        yield code

def get_region_numeric(code):
    """
    Given a UN Statistics Division region code as a string or integer,
    returns the code as an integer.

    Raises :exc:`KeyError` if the region code is unrecognized.
    """
    v = code
    if isinstance(v, int):
        if v in _region_countries:
            return v
    elif isinstance(v, str):
        try:
            v = int(v)
            if v in _region_countries:
                return v
        except:
            pass
    raise KeyError("Unknown region ID %s" % repr(code))

def get_region_name(code):
    """
    Given a region code as a string or integer, returns the name for
    the region.

    Raises :exc:`KeyError` if the region code is unrecognized.
    """
    return _area_name[get_region_numeric(code)]

def get_region_tlds(code):
    """
    Given a region code as a string or integer, returns a list of zero
    or more DNS top-level domains for that region.

    Raises :exc:`KeyError` if the region code is unrecognized.
    """
    return _area_tlds.get(get_region_numeric(code), [])

def iter_regions():
    """
    Returns an iterator which yields all top-level UN Statistics
    Division numeric region codes as integers.  This includes Africa,
    the Americas, Asia, Europe, Oceania, and Other.
    """
    for code in _region_list:
        if _region_superregion[code] == None:
            yield code

def iter_region_subregions(code):
    """
    Given the code for a containing region, returns an iterator which
    yields all second-level UN Statistics Division numeric region
    codes as integers.

    Raises :exc:`KeyError` if the region code is unrecognized.
    """
    get_region_numeric(code)
    def gen():
        for subcode in _region_subregions[get_region_numeric(code)]:
            yield subcode
    return gen()

def iter_region_countries(code):
    """
    Given the code for a containing region, returns an iterator which
    yields as integers all ISO 3166-1 numeric country codes that are
    part of that region.
    """
    get_region_numeric(code)
    def gen():
        for country_code in _region_countries[get_region_numeric(code)]:
            yield country_code
    return gen()

__all__ = """

    get_area_numeric
    get_area_name
    get_area_tlds

    get_country_numeric
    get_country_name
    get_country_alpha2
    get_country_alpha3
    get_country_tlds
    get_country_region
    get_country_subregion
    iter_countries

    get_region_numeric
    get_region_name
    get_region_tlds
    iter_regions
    iter_region_subregions
    iter_region_countries

""".split()
