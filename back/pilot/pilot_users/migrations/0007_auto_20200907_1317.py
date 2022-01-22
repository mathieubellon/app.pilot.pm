# Generated by Django 2.2.14 on 2020-09-07 11:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pilot_users', '0006_auto_20190930_1650'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pilotuser',
            name='first_name',
            field=models.CharField(blank=True, max_length=80, verbose_name='Prénom'),
        ),
        migrations.AlterField(
            model_name='pilotuser',
            name='last_name',
            field=models.CharField(blank=True, max_length=80, verbose_name='Nom'),
        ),
        migrations.AlterField(
            model_name='pilotuser',
            name='timezone',
            field=models.CharField(choices=[('Pacific/Midway', '[UTC-11:00] Pacific/Midway'), ('Pacific/Niue', '[UTC-11:00] Pacific/Niue'), ('Pacific/Pago_Pago', '[UTC-11:00] Pacific/Pago_Pago'), ('Pacific/Honolulu', '[UTC-10:00] Pacific/Honolulu'), ('Pacific/Rarotonga', '[UTC-10:00] Pacific/Rarotonga'), ('Pacific/Tahiti', '[UTC-10:00] Pacific/Tahiti'), ('US/Hawaii', '[UTC-10:00] US/Hawaii'), ('Pacific/Marquesas', '[UTC-09:30] Pacific/Marquesas'), ('America/Adak', '[UTC-09:00] America/Adak'), ('Pacific/Gambier', '[UTC-09:00] Pacific/Gambier'), ('America/Anchorage', '[UTC-08:00] America/Anchorage'), ('America/Juneau', '[UTC-08:00] America/Juneau'), ('America/Metlakatla', '[UTC-08:00] America/Metlakatla'), ('America/Nome', '[UTC-08:00] America/Nome'), ('America/Sitka', '[UTC-08:00] America/Sitka'), ('America/Yakutat', '[UTC-08:00] America/Yakutat'), ('Pacific/Pitcairn', '[UTC-08:00] Pacific/Pitcairn'), ('US/Alaska', '[UTC-08:00] US/Alaska'), ('America/Creston', '[UTC-07:00] America/Creston'), ('America/Dawson', '[UTC-07:00] America/Dawson'), ('America/Dawson_Creek', '[UTC-07:00] America/Dawson_Creek'), ('America/Fort_Nelson', '[UTC-07:00] America/Fort_Nelson'), ('America/Hermosillo', '[UTC-07:00] America/Hermosillo'), ('America/Los_Angeles', '[UTC-07:00] America/Los_Angeles'), ('America/Phoenix', '[UTC-07:00] America/Phoenix'), ('America/Tijuana', '[UTC-07:00] America/Tijuana'), ('America/Vancouver', '[UTC-07:00] America/Vancouver'), ('America/Whitehorse', '[UTC-07:00] America/Whitehorse'), ('Canada/Pacific', '[UTC-07:00] Canada/Pacific'), ('US/Arizona', '[UTC-07:00] US/Arizona'), ('US/Pacific', '[UTC-07:00] US/Pacific'), ('America/Belize', '[UTC-06:00] America/Belize'), ('America/Boise', '[UTC-06:00] America/Boise'), ('America/Cambridge_Bay', '[UTC-06:00] America/Cambridge_Bay'), ('America/Chihuahua', '[UTC-06:00] America/Chihuahua'), ('America/Costa_Rica', '[UTC-06:00] America/Costa_Rica'), ('America/Denver', '[UTC-06:00] America/Denver'), ('America/Edmonton', '[UTC-06:00] America/Edmonton'), ('America/El_Salvador', '[UTC-06:00] America/El_Salvador'), ('America/Guatemala', '[UTC-06:00] America/Guatemala'), ('America/Inuvik', '[UTC-06:00] America/Inuvik'), ('America/Managua', '[UTC-06:00] America/Managua'), ('America/Mazatlan', '[UTC-06:00] America/Mazatlan'), ('America/Ojinaga', '[UTC-06:00] America/Ojinaga'), ('America/Regina', '[UTC-06:00] America/Regina'), ('America/Swift_Current', '[UTC-06:00] America/Swift_Current'), ('America/Tegucigalpa', '[UTC-06:00] America/Tegucigalpa'), ('America/Yellowknife', '[UTC-06:00] America/Yellowknife'), ('Canada/Mountain', '[UTC-06:00] Canada/Mountain'), ('Pacific/Galapagos', '[UTC-06:00] Pacific/Galapagos'), ('US/Mountain', '[UTC-06:00] US/Mountain'), ('America/Atikokan', '[UTC-05:00] America/Atikokan'), ('America/Bahia_Banderas', '[UTC-05:00] America/Bahia_Banderas'), ('America/Bogota', '[UTC-05:00] America/Bogota'), ('America/Cancun', '[UTC-05:00] America/Cancun'), ('America/Cayman', '[UTC-05:00] America/Cayman'), ('America/Chicago', '[UTC-05:00] America/Chicago'), ('America/Eirunepe', '[UTC-05:00] America/Eirunepe'), ('America/Guayaquil', '[UTC-05:00] America/Guayaquil'), ('America/Indiana/Knox', '[UTC-05:00] America/Indiana/Knox'), ('America/Indiana/Tell_City', '[UTC-05:00] America/Indiana/Tell_City'), ('America/Jamaica', '[UTC-05:00] America/Jamaica'), ('America/Lima', '[UTC-05:00] America/Lima'), ('America/Matamoros', '[UTC-05:00] America/Matamoros'), ('America/Menominee', '[UTC-05:00] America/Menominee'), ('America/Merida', '[UTC-05:00] America/Merida'), ('America/Mexico_City', '[UTC-05:00] America/Mexico_City'), ('America/Monterrey', '[UTC-05:00] America/Monterrey'), ('America/North_Dakota/Beulah', '[UTC-05:00] America/North_Dakota/Beulah'), ('America/North_Dakota/Center', '[UTC-05:00] America/North_Dakota/Center'), ('America/North_Dakota/New_Salem', '[UTC-05:00] America/North_Dakota/New_Salem'), ('America/Panama', '[UTC-05:00] America/Panama'), ('America/Rainy_River', '[UTC-05:00] America/Rainy_River'), ('America/Rankin_Inlet', '[UTC-05:00] America/Rankin_Inlet'), ('America/Resolute', '[UTC-05:00] America/Resolute'), ('America/Rio_Branco', '[UTC-05:00] America/Rio_Branco'), ('America/Winnipeg', '[UTC-05:00] America/Winnipeg'), ('Canada/Central', '[UTC-05:00] Canada/Central'), ('Pacific/Easter', '[UTC-05:00] Pacific/Easter'), ('US/Central', '[UTC-05:00] US/Central'), ('America/Anguilla', '[UTC-04:00] America/Anguilla'), ('America/Antigua', '[UTC-04:00] America/Antigua'), ('America/Aruba', '[UTC-04:00] America/Aruba'), ('America/Asuncion', '[UTC-04:00] America/Asuncion'), ('America/Barbados', '[UTC-04:00] America/Barbados'), ('America/Blanc-Sablon', '[UTC-04:00] America/Blanc-Sablon'), ('America/Boa_Vista', '[UTC-04:00] America/Boa_Vista'), ('America/Campo_Grande', '[UTC-04:00] America/Campo_Grande'), ('America/Caracas', '[UTC-04:00] America/Caracas'), ('America/Cuiaba', '[UTC-04:00] America/Cuiaba'), ('America/Curacao', '[UTC-04:00] America/Curacao'), ('America/Detroit', '[UTC-04:00] America/Detroit'), ('America/Dominica', '[UTC-04:00] America/Dominica'), ('America/Grand_Turk', '[UTC-04:00] America/Grand_Turk'), ('America/Grenada', '[UTC-04:00] America/Grenada'), ('America/Guadeloupe', '[UTC-04:00] America/Guadeloupe'), ('America/Guyana', '[UTC-04:00] America/Guyana'), ('America/Havana', '[UTC-04:00] America/Havana'), ('America/Indiana/Indianapolis', '[UTC-04:00] America/Indiana/Indianapolis'), ('America/Indiana/Marengo', '[UTC-04:00] America/Indiana/Marengo'), ('America/Indiana/Petersburg', '[UTC-04:00] America/Indiana/Petersburg'), ('America/Indiana/Vevay', '[UTC-04:00] America/Indiana/Vevay'), ('America/Indiana/Vincennes', '[UTC-04:00] America/Indiana/Vincennes'), ('America/Indiana/Winamac', '[UTC-04:00] America/Indiana/Winamac'), ('America/Iqaluit', '[UTC-04:00] America/Iqaluit'), ('America/Kentucky/Louisville', '[UTC-04:00] America/Kentucky/Louisville'), ('America/Kentucky/Monticello', '[UTC-04:00] America/Kentucky/Monticello'), ('America/Kralendijk', '[UTC-04:00] America/Kralendijk'), ('America/La_Paz', '[UTC-04:00] America/La_Paz'), ('America/Lower_Princes', '[UTC-04:00] America/Lower_Princes'), ('America/Manaus', '[UTC-04:00] America/Manaus'), ('America/Marigot', '[UTC-04:00] America/Marigot'), ('America/Martinique', '[UTC-04:00] America/Martinique'), ('America/Montserrat', '[UTC-04:00] America/Montserrat'), ('America/Nassau', '[UTC-04:00] America/Nassau'), ('America/New_York', '[UTC-04:00] America/New_York'), ('America/Nipigon', '[UTC-04:00] America/Nipigon'), ('America/Pangnirtung', '[UTC-04:00] America/Pangnirtung'), ('America/Port-au-Prince', '[UTC-04:00] America/Port-au-Prince'), ('America/Port_of_Spain', '[UTC-04:00] America/Port_of_Spain'), ('America/Porto_Velho', '[UTC-04:00] America/Porto_Velho'), ('America/Puerto_Rico', '[UTC-04:00] America/Puerto_Rico'), ('America/Santo_Domingo', '[UTC-04:00] America/Santo_Domingo'), ('America/St_Barthelemy', '[UTC-04:00] America/St_Barthelemy'), ('America/St_Kitts', '[UTC-04:00] America/St_Kitts'), ('America/St_Lucia', '[UTC-04:00] America/St_Lucia'), ('America/St_Thomas', '[UTC-04:00] America/St_Thomas'), ('America/St_Vincent', '[UTC-04:00] America/St_Vincent'), ('America/Thunder_Bay', '[UTC-04:00] America/Thunder_Bay'), ('America/Toronto', '[UTC-04:00] America/Toronto'), ('America/Tortola', '[UTC-04:00] America/Tortola'), ('Canada/Eastern', '[UTC-04:00] Canada/Eastern'), ('US/Eastern', '[UTC-04:00] US/Eastern'), ('America/Araguaina', '[UTC-03:00] America/Araguaina'), ('America/Argentina/Buenos_Aires', '[UTC-03:00] America/Argentina/Buenos_Aires'), ('America/Argentina/Catamarca', '[UTC-03:00] America/Argentina/Catamarca'), ('America/Argentina/Cordoba', '[UTC-03:00] America/Argentina/Cordoba'), ('America/Argentina/Jujuy', '[UTC-03:00] America/Argentina/Jujuy'), ('America/Argentina/La_Rioja', '[UTC-03:00] America/Argentina/La_Rioja'), ('America/Argentina/Mendoza', '[UTC-03:00] America/Argentina/Mendoza'), ('America/Argentina/Rio_Gallegos', '[UTC-03:00] America/Argentina/Rio_Gallegos'), ('America/Argentina/Salta', '[UTC-03:00] America/Argentina/Salta'), ('America/Argentina/San_Juan', '[UTC-03:00] America/Argentina/San_Juan'), ('America/Argentina/San_Luis', '[UTC-03:00] America/Argentina/San_Luis'), ('America/Argentina/Tucuman', '[UTC-03:00] America/Argentina/Tucuman'), ('America/Argentina/Ushuaia', '[UTC-03:00] America/Argentina/Ushuaia'), ('America/Bahia', '[UTC-03:00] America/Bahia'), ('America/Belem', '[UTC-03:00] America/Belem'), ('America/Cayenne', '[UTC-03:00] America/Cayenne'), ('America/Fortaleza', '[UTC-03:00] America/Fortaleza'), ('America/Glace_Bay', '[UTC-03:00] America/Glace_Bay'), ('America/Goose_Bay', '[UTC-03:00] America/Goose_Bay'), ('America/Halifax', '[UTC-03:00] America/Halifax'), ('America/Maceio', '[UTC-03:00] America/Maceio'), ('America/Moncton', '[UTC-03:00] America/Moncton'), ('America/Montevideo', '[UTC-03:00] America/Montevideo'), ('America/Paramaribo', '[UTC-03:00] America/Paramaribo'), ('America/Punta_Arenas', '[UTC-03:00] America/Punta_Arenas'), ('America/Recife', '[UTC-03:00] America/Recife'), ('America/Santarem', '[UTC-03:00] America/Santarem'), ('America/Santiago', '[UTC-03:00] America/Santiago'), ('America/Sao_Paulo', '[UTC-03:00] America/Sao_Paulo'), ('America/Thule', '[UTC-03:00] America/Thule'), ('Antarctica/Palmer', '[UTC-03:00] Antarctica/Palmer'), ('Antarctica/Rothera', '[UTC-03:00] Antarctica/Rothera'), ('Atlantic/Bermuda', '[UTC-03:00] Atlantic/Bermuda'), ('Atlantic/Stanley', '[UTC-03:00] Atlantic/Stanley'), ('Canada/Atlantic', '[UTC-03:00] Canada/Atlantic'), ('America/St_Johns', '[UTC-02:30] America/St_Johns'), ('Canada/Newfoundland', '[UTC-02:30] Canada/Newfoundland'), ('America/Godthab', '[UTC-02:00] America/Godthab'), ('America/Miquelon', '[UTC-02:00] America/Miquelon'), ('America/Noronha', '[UTC-02:00] America/Noronha'), ('Atlantic/South_Georgia', '[UTC-02:00] Atlantic/South_Georgia'), ('Atlantic/Cape_Verde', '[UTC-01:00] Atlantic/Cape_Verde'), ('Africa/Abidjan', '[UTC+00:00] Africa/Abidjan'), ('Africa/Accra', '[UTC+00:00] Africa/Accra'), ('Africa/Bamako', '[UTC+00:00] Africa/Bamako'), ('Africa/Banjul', '[UTC+00:00] Africa/Banjul'), ('Africa/Bissau', '[UTC+00:00] Africa/Bissau'), ('Africa/Conakry', '[UTC+00:00] Africa/Conakry'), ('Africa/Dakar', '[UTC+00:00] Africa/Dakar'), ('Africa/Freetown', '[UTC+00:00] Africa/Freetown'), ('Africa/Lome', '[UTC+00:00] Africa/Lome'), ('Africa/Monrovia', '[UTC+00:00] Africa/Monrovia'), ('Africa/Nouakchott', '[UTC+00:00] Africa/Nouakchott'), ('Africa/Ouagadougou', '[UTC+00:00] Africa/Ouagadougou'), ('Africa/Sao_Tome', '[UTC+00:00] Africa/Sao_Tome'), ('America/Danmarkshavn', '[UTC+00:00] America/Danmarkshavn'), ('America/Scoresbysund', '[UTC+00:00] America/Scoresbysund'), ('Atlantic/Azores', '[UTC+00:00] Atlantic/Azores'), ('Atlantic/Reykjavik', '[UTC+00:00] Atlantic/Reykjavik'), ('Atlantic/St_Helena', '[UTC+00:00] Atlantic/St_Helena'), ('Africa/Algiers', '[UTC+01:00] Africa/Algiers'), ('Africa/Bangui', '[UTC+01:00] Africa/Bangui'), ('Africa/Brazzaville', '[UTC+01:00] Africa/Brazzaville'), ('Africa/Casablanca', '[UTC+01:00] Africa/Casablanca'), ('Africa/Douala', '[UTC+01:00] Africa/Douala'), ('Africa/El_Aaiun', '[UTC+01:00] Africa/El_Aaiun'), ('Africa/Kinshasa', '[UTC+01:00] Africa/Kinshasa'), ('Africa/Lagos', '[UTC+01:00] Africa/Lagos'), ('Africa/Libreville', '[UTC+01:00] Africa/Libreville'), ('Africa/Luanda', '[UTC+01:00] Africa/Luanda'), ('Africa/Malabo', '[UTC+01:00] Africa/Malabo'), ('Africa/Ndjamena', '[UTC+01:00] Africa/Ndjamena'), ('Africa/Niamey', '[UTC+01:00] Africa/Niamey'), ('Africa/Porto-Novo', '[UTC+01:00] Africa/Porto-Novo'), ('Africa/Tunis', '[UTC+01:00] Africa/Tunis'), ('Atlantic/Canary', '[UTC+01:00] Atlantic/Canary'), ('Atlantic/Faroe', '[UTC+01:00] Atlantic/Faroe'), ('Atlantic/Madeira', '[UTC+01:00] Atlantic/Madeira'), ('Europe/Dublin', '[UTC+01:00] Europe/Dublin'), ('Europe/Guernsey', '[UTC+01:00] Europe/Guernsey'), ('Europe/Isle_of_Man', '[UTC+01:00] Europe/Isle_of_Man'), ('Europe/Jersey', '[UTC+01:00] Europe/Jersey'), ('Europe/Lisbon', '[UTC+01:00] Europe/Lisbon'), ('Europe/London', '[UTC+01:00] Europe/London'), ('Africa/Blantyre', '[UTC+02:00] Africa/Blantyre'), ('Africa/Bujumbura', '[UTC+02:00] Africa/Bujumbura'), ('Africa/Cairo', '[UTC+02:00] Africa/Cairo'), ('Africa/Ceuta', '[UTC+02:00] Africa/Ceuta'), ('Africa/Gaborone', '[UTC+02:00] Africa/Gaborone'), ('Africa/Harare', '[UTC+02:00] Africa/Harare'), ('Africa/Johannesburg', '[UTC+02:00] Africa/Johannesburg'), ('Africa/Khartoum', '[UTC+02:00] Africa/Khartoum'), ('Africa/Kigali', '[UTC+02:00] Africa/Kigali'), ('Africa/Lubumbashi', '[UTC+02:00] Africa/Lubumbashi'), ('Africa/Lusaka', '[UTC+02:00] Africa/Lusaka'), ('Africa/Maputo', '[UTC+02:00] Africa/Maputo'), ('Africa/Maseru', '[UTC+02:00] Africa/Maseru'), ('Africa/Mbabane', '[UTC+02:00] Africa/Mbabane'), ('Africa/Tripoli', '[UTC+02:00] Africa/Tripoli'), ('Africa/Windhoek', '[UTC+02:00] Africa/Windhoek'), ('Antarctica/Troll', '[UTC+02:00] Antarctica/Troll'), ('Arctic/Longyearbyen', '[UTC+02:00] Arctic/Longyearbyen'), ('Europe/Amsterdam', '[UTC+02:00] Europe/Amsterdam'), ('Europe/Andorra', '[UTC+02:00] Europe/Andorra'), ('Europe/Belgrade', '[UTC+02:00] Europe/Belgrade'), ('Europe/Berlin', '[UTC+02:00] Europe/Berlin'), ('Europe/Bratislava', '[UTC+02:00] Europe/Bratislava'), ('Europe/Brussels', '[UTC+02:00] Europe/Brussels'), ('Europe/Budapest', '[UTC+02:00] Europe/Budapest'), ('Europe/Busingen', '[UTC+02:00] Europe/Busingen'), ('Europe/Copenhagen', '[UTC+02:00] Europe/Copenhagen'), ('Europe/Gibraltar', '[UTC+02:00] Europe/Gibraltar'), ('Europe/Kaliningrad', '[UTC+02:00] Europe/Kaliningrad'), ('Europe/Ljubljana', '[UTC+02:00] Europe/Ljubljana'), ('Europe/Luxembourg', '[UTC+02:00] Europe/Luxembourg'), ('Europe/Madrid', '[UTC+02:00] Europe/Madrid'), ('Europe/Malta', '[UTC+02:00] Europe/Malta'), ('Europe/Monaco', '[UTC+02:00] Europe/Monaco'), ('Europe/Oslo', '[UTC+02:00] Europe/Oslo'), ('Europe/Paris', '[UTC+02:00] Europe/Paris'), ('Europe/Podgorica', '[UTC+02:00] Europe/Podgorica'), ('Europe/Prague', '[UTC+02:00] Europe/Prague'), ('Europe/Rome', '[UTC+02:00] Europe/Rome'), ('Europe/San_Marino', '[UTC+02:00] Europe/San_Marino'), ('Europe/Sarajevo', '[UTC+02:00] Europe/Sarajevo'), ('Europe/Skopje', '[UTC+02:00] Europe/Skopje'), ('Europe/Stockholm', '[UTC+02:00] Europe/Stockholm'), ('Europe/Tirane', '[UTC+02:00] Europe/Tirane'), ('Europe/Vaduz', '[UTC+02:00] Europe/Vaduz'), ('Europe/Vatican', '[UTC+02:00] Europe/Vatican'), ('Europe/Vienna', '[UTC+02:00] Europe/Vienna'), ('Europe/Warsaw', '[UTC+02:00] Europe/Warsaw'), ('Europe/Zagreb', '[UTC+02:00] Europe/Zagreb'), ('Europe/Zurich', '[UTC+02:00] Europe/Zurich'), ('Africa/Addis_Ababa', '[UTC+03:00] Africa/Addis_Ababa'), ('Africa/Asmara', '[UTC+03:00] Africa/Asmara'), ('Africa/Dar_es_Salaam', '[UTC+03:00] Africa/Dar_es_Salaam'), ('Africa/Djibouti', '[UTC+03:00] Africa/Djibouti'), ('Africa/Juba', '[UTC+03:00] Africa/Juba'), ('Africa/Kampala', '[UTC+03:00] Africa/Kampala'), ('Africa/Mogadishu', '[UTC+03:00] Africa/Mogadishu'), ('Africa/Nairobi', '[UTC+03:00] Africa/Nairobi'), ('Antarctica/Syowa', '[UTC+03:00] Antarctica/Syowa'), ('Asia/Aden', '[UTC+03:00] Asia/Aden'), ('Asia/Amman', '[UTC+03:00] Asia/Amman'), ('Asia/Baghdad', '[UTC+03:00] Asia/Baghdad'), ('Asia/Bahrain', '[UTC+03:00] Asia/Bahrain'), ('Asia/Beirut', '[UTC+03:00] Asia/Beirut'), ('Asia/Damascus', '[UTC+03:00] Asia/Damascus'), ('Asia/Famagusta', '[UTC+03:00] Asia/Famagusta'), ('Asia/Gaza', '[UTC+03:00] Asia/Gaza'), ('Asia/Hebron', '[UTC+03:00] Asia/Hebron'), ('Asia/Jerusalem', '[UTC+03:00] Asia/Jerusalem'), ('Asia/Kuwait', '[UTC+03:00] Asia/Kuwait'), ('Asia/Nicosia', '[UTC+03:00] Asia/Nicosia'), ('Asia/Qatar', '[UTC+03:00] Asia/Qatar'), ('Asia/Riyadh', '[UTC+03:00] Asia/Riyadh'), ('Europe/Athens', '[UTC+03:00] Europe/Athens'), ('Europe/Bucharest', '[UTC+03:00] Europe/Bucharest'), ('Europe/Chisinau', '[UTC+03:00] Europe/Chisinau'), ('Europe/Helsinki', '[UTC+03:00] Europe/Helsinki'), ('Europe/Istanbul', '[UTC+03:00] Europe/Istanbul'), ('Europe/Kiev', '[UTC+03:00] Europe/Kiev'), ('Europe/Kirov', '[UTC+03:00] Europe/Kirov'), ('Europe/Mariehamn', '[UTC+03:00] Europe/Mariehamn'), ('Europe/Minsk', '[UTC+03:00] Europe/Minsk'), ('Europe/Moscow', '[UTC+03:00] Europe/Moscow'), ('Europe/Riga', '[UTC+03:00] Europe/Riga'), ('Europe/Simferopol', '[UTC+03:00] Europe/Simferopol'), ('Europe/Sofia', '[UTC+03:00] Europe/Sofia'), ('Europe/Tallinn', '[UTC+03:00] Europe/Tallinn'), ('Europe/Uzhgorod', '[UTC+03:00] Europe/Uzhgorod'), ('Europe/Vilnius', '[UTC+03:00] Europe/Vilnius'), ('Europe/Zaporozhye', '[UTC+03:00] Europe/Zaporozhye'), ('Indian/Antananarivo', '[UTC+03:00] Indian/Antananarivo'), ('Indian/Comoro', '[UTC+03:00] Indian/Comoro'), ('Indian/Mayotte', '[UTC+03:00] Indian/Mayotte'), ('Asia/Baku', '[UTC+04:00] Asia/Baku'), ('Asia/Dubai', '[UTC+04:00] Asia/Dubai'), ('Asia/Muscat', '[UTC+04:00] Asia/Muscat'), ('Asia/Tbilisi', '[UTC+04:00] Asia/Tbilisi'), ('Asia/Yerevan', '[UTC+04:00] Asia/Yerevan'), ('Europe/Astrakhan', '[UTC+04:00] Europe/Astrakhan'), ('Europe/Samara', '[UTC+04:00] Europe/Samara'), ('Europe/Saratov', '[UTC+04:00] Europe/Saratov'), ('Europe/Ulyanovsk', '[UTC+04:00] Europe/Ulyanovsk'), ('Europe/Volgograd', '[UTC+04:00] Europe/Volgograd'), ('Indian/Mahe', '[UTC+04:00] Indian/Mahe'), ('Indian/Mauritius', '[UTC+04:00] Indian/Mauritius'), ('Indian/Reunion', '[UTC+04:00] Indian/Reunion'), ('Asia/Kabul', '[UTC+04:30] Asia/Kabul'), ('Asia/Tehran', '[UTC+04:30] Asia/Tehran'), ('Antarctica/Mawson', '[UTC+05:00] Antarctica/Mawson'), ('Asia/Aqtau', '[UTC+05:00] Asia/Aqtau'), ('Asia/Aqtobe', '[UTC+05:00] Asia/Aqtobe'), ('Asia/Ashgabat', '[UTC+05:00] Asia/Ashgabat'), ('Asia/Atyrau', '[UTC+05:00] Asia/Atyrau'), ('Asia/Dushanbe', '[UTC+05:00] Asia/Dushanbe'), ('Asia/Karachi', '[UTC+05:00] Asia/Karachi'), ('Asia/Oral', '[UTC+05:00] Asia/Oral'), ('Asia/Qyzylorda', '[UTC+05:00] Asia/Qyzylorda'), ('Asia/Samarkand', '[UTC+05:00] Asia/Samarkand'), ('Asia/Tashkent', '[UTC+05:00] Asia/Tashkent'), ('Asia/Yekaterinburg', '[UTC+05:00] Asia/Yekaterinburg'), ('Indian/Kerguelen', '[UTC+05:00] Indian/Kerguelen'), ('Indian/Maldives', '[UTC+05:00] Indian/Maldives'), ('Asia/Colombo', '[UTC+05:30] Asia/Colombo'), ('Asia/Kolkata', '[UTC+05:30] Asia/Kolkata'), ('Asia/Kathmandu', '[UTC+05:45] Asia/Kathmandu'), ('Antarctica/Vostok', '[UTC+06:00] Antarctica/Vostok'), ('Asia/Almaty', '[UTC+06:00] Asia/Almaty'), ('Asia/Bishkek', '[UTC+06:00] Asia/Bishkek'), ('Asia/Dhaka', '[UTC+06:00] Asia/Dhaka'), ('Asia/Omsk', '[UTC+06:00] Asia/Omsk'), ('Asia/Qostanay', '[UTC+06:00] Asia/Qostanay'), ('Asia/Thimphu', '[UTC+06:00] Asia/Thimphu'), ('Asia/Urumqi', '[UTC+06:00] Asia/Urumqi'), ('Indian/Chagos', '[UTC+06:00] Indian/Chagos'), ('Asia/Yangon', '[UTC+06:30] Asia/Yangon'), ('Indian/Cocos', '[UTC+06:30] Indian/Cocos'), ('Antarctica/Davis', '[UTC+07:00] Antarctica/Davis'), ('Asia/Bangkok', '[UTC+07:00] Asia/Bangkok'), ('Asia/Barnaul', '[UTC+07:00] Asia/Barnaul'), ('Asia/Ho_Chi_Minh', '[UTC+07:00] Asia/Ho_Chi_Minh'), ('Asia/Hovd', '[UTC+07:00] Asia/Hovd'), ('Asia/Jakarta', '[UTC+07:00] Asia/Jakarta'), ('Asia/Krasnoyarsk', '[UTC+07:00] Asia/Krasnoyarsk'), ('Asia/Novokuznetsk', '[UTC+07:00] Asia/Novokuznetsk'), ('Asia/Novosibirsk', '[UTC+07:00] Asia/Novosibirsk'), ('Asia/Phnom_Penh', '[UTC+07:00] Asia/Phnom_Penh'), ('Asia/Pontianak', '[UTC+07:00] Asia/Pontianak'), ('Asia/Tomsk', '[UTC+07:00] Asia/Tomsk'), ('Asia/Vientiane', '[UTC+07:00] Asia/Vientiane'), ('Indian/Christmas', '[UTC+07:00] Indian/Christmas'), ('Antarctica/Casey', '[UTC+08:00] Antarctica/Casey'), ('Asia/Brunei', '[UTC+08:00] Asia/Brunei'), ('Asia/Choibalsan', '[UTC+08:00] Asia/Choibalsan'), ('Asia/Hong_Kong', '[UTC+08:00] Asia/Hong_Kong'), ('Asia/Irkutsk', '[UTC+08:00] Asia/Irkutsk'), ('Asia/Kuala_Lumpur', '[UTC+08:00] Asia/Kuala_Lumpur'), ('Asia/Kuching', '[UTC+08:00] Asia/Kuching'), ('Asia/Macau', '[UTC+08:00] Asia/Macau'), ('Asia/Makassar', '[UTC+08:00] Asia/Makassar'), ('Asia/Manila', '[UTC+08:00] Asia/Manila'), ('Asia/Shanghai', '[UTC+08:00] Asia/Shanghai'), ('Asia/Singapore', '[UTC+08:00] Asia/Singapore'), ('Asia/Taipei', '[UTC+08:00] Asia/Taipei'), ('Asia/Ulaanbaatar', '[UTC+08:00] Asia/Ulaanbaatar'), ('Australia/Perth', '[UTC+08:00] Australia/Perth'), ('Australia/Eucla', '[UTC+08:45] Australia/Eucla'), ('Asia/Chita', '[UTC+09:00] Asia/Chita'), ('Asia/Dili', '[UTC+09:00] Asia/Dili'), ('Asia/Jayapura', '[UTC+09:00] Asia/Jayapura'), ('Asia/Khandyga', '[UTC+09:00] Asia/Khandyga'), ('Asia/Pyongyang', '[UTC+09:00] Asia/Pyongyang'), ('Asia/Seoul', '[UTC+09:00] Asia/Seoul'), ('Asia/Tokyo', '[UTC+09:00] Asia/Tokyo'), ('Asia/Yakutsk', '[UTC+09:00] Asia/Yakutsk'), ('Pacific/Palau', '[UTC+09:00] Pacific/Palau'), ('Australia/Adelaide', '[UTC+09:30] Australia/Adelaide'), ('Australia/Broken_Hill', '[UTC+09:30] Australia/Broken_Hill'), ('Australia/Darwin', '[UTC+09:30] Australia/Darwin'), ('Antarctica/DumontDUrville', '[UTC+10:00] Antarctica/DumontDUrville'), ('Asia/Ust-Nera', '[UTC+10:00] Asia/Ust-Nera'), ('Asia/Vladivostok', '[UTC+10:00] Asia/Vladivostok'), ('Australia/Brisbane', '[UTC+10:00] Australia/Brisbane'), ('Australia/Currie', '[UTC+10:00] Australia/Currie'), ('Australia/Hobart', '[UTC+10:00] Australia/Hobart'), ('Australia/Lindeman', '[UTC+10:00] Australia/Lindeman'), ('Australia/Melbourne', '[UTC+10:00] Australia/Melbourne'), ('Australia/Sydney', '[UTC+10:00] Australia/Sydney'), ('Pacific/Chuuk', '[UTC+10:00] Pacific/Chuuk'), ('Pacific/Guam', '[UTC+10:00] Pacific/Guam'), ('Pacific/Port_Moresby', '[UTC+10:00] Pacific/Port_Moresby'), ('Pacific/Saipan', '[UTC+10:00] Pacific/Saipan'), ('Australia/Lord_Howe', '[UTC+10:30] Australia/Lord_Howe'), ('Antarctica/Macquarie', '[UTC+11:00] Antarctica/Macquarie'), ('Asia/Magadan', '[UTC+11:00] Asia/Magadan'), ('Asia/Sakhalin', '[UTC+11:00] Asia/Sakhalin'), ('Asia/Srednekolymsk', '[UTC+11:00] Asia/Srednekolymsk'), ('Pacific/Bougainville', '[UTC+11:00] Pacific/Bougainville'), ('Pacific/Efate', '[UTC+11:00] Pacific/Efate'), ('Pacific/Guadalcanal', '[UTC+11:00] Pacific/Guadalcanal'), ('Pacific/Kosrae', '[UTC+11:00] Pacific/Kosrae'), ('Pacific/Norfolk', '[UTC+11:00] Pacific/Norfolk'), ('Pacific/Noumea', '[UTC+11:00] Pacific/Noumea'), ('Pacific/Pohnpei', '[UTC+11:00] Pacific/Pohnpei'), ('Antarctica/McMurdo', '[UTC+12:00] Antarctica/McMurdo'), ('Asia/Anadyr', '[UTC+12:00] Asia/Anadyr'), ('Asia/Kamchatka', '[UTC+12:00] Asia/Kamchatka'), ('Pacific/Auckland', '[UTC+12:00] Pacific/Auckland'), ('Pacific/Fiji', '[UTC+12:00] Pacific/Fiji'), ('Pacific/Funafuti', '[UTC+12:00] Pacific/Funafuti'), ('Pacific/Kwajalein', '[UTC+12:00] Pacific/Kwajalein'), ('Pacific/Majuro', '[UTC+12:00] Pacific/Majuro'), ('Pacific/Nauru', '[UTC+12:00] Pacific/Nauru'), ('Pacific/Tarawa', '[UTC+12:00] Pacific/Tarawa'), ('Pacific/Wake', '[UTC+12:00] Pacific/Wake'), ('Pacific/Wallis', '[UTC+12:00] Pacific/Wallis'), ('Pacific/Chatham', '[UTC+12:45] Pacific/Chatham'), ('Pacific/Apia', '[UTC+13:00] Pacific/Apia'), ('Pacific/Enderbury', '[UTC+13:00] Pacific/Enderbury'), ('Pacific/Fakaofo', '[UTC+13:00] Pacific/Fakaofo'), ('Pacific/Tongatapu', '[UTC+13:00] Pacific/Tongatapu'), ('Pacific/Kiritimati', '[UTC+14:00] Pacific/Kiritimati')], default='Europe/Paris', max_length=50, verbose_name='Fuseau horaire'),
        ),
    ]
