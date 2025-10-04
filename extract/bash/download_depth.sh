#!/bin/bash

GREP_OPTIONS=''

cookiejar=$(mktemp cookies.XXXXXXXXXX)
netrc=$(mktemp netrc.XXXXXXXXXX)
chmod 0600 "$cookiejar" "$netrc"
function finish {
  rm -rf "$cookiejar" "$netrc"
}

trap finish EXIT
WGETRC="$wgetrc"

prompt_credentials() {
    echo "Enter your Earthdata Login or other provider supplied credentials"
    read -p "Username (lrodriguez22): " username
    username=${username:-lrodriguez22}
    read -s -p "Password: " password
    echo "machine urs.earthdata.nasa.gov login $username password $password" >> $netrc
    echo
}

exit_with_error() {
    echo
    echo "Unable to Retrieve Data"
    echo
    echo $1
    echo
    echo "https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107234251_08052501_006_01_001_01.h5"
    echo
    exit 1
}

prompt_credentials
  detect_app_approval() {
    approved=`curl -s -b "$cookiejar" -c "$cookiejar" -L --max-redirs 5 --netrc-file "$netrc" https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107234251_08052501_006_01_001_01.h5 -w '\n%{http_code}' | tail  -1`
    if [ "$approved" -ne "200" ] && [ "$approved" -ne "301" ] && [ "$approved" -ne "302" ]; then
        # User didn't approve the app. Direct users to approve the app in URS
        exit_with_error "Please ensure that you have authorized the remote application by visiting the link below "
    fi
}

setup_auth_curl() {
    # Firstly, check if it require URS authentication
    status=$(curl -s -z "$(date)" -w '\n%{http_code}' https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107234251_08052501_006_01_001_01.h5 | tail -1)
    if [[ "$status" -ne "200" && "$status" -ne "304" ]]; then
        # URS authentication is required. Now further check if the application/remote service is approved.
        detect_app_approval
    fi
}

setup_auth_wget() {
    # The safest way to auth via curl is netrc. Note: there's no checking or feedback
    # if login is unsuccessful
    touch ~/.netrc
    chmod 0600 ~/.netrc
    credentials=$(grep 'machine urs.earthdata.nasa.gov' ~/.netrc)
    if [ -z "$credentials" ]; then
        cat "$netrc" >> ~/.netrc
    fi
}

fetch_urls() {
  if command -v curl >/dev/null 2>&1; then
      setup_auth_curl
      while read -r line; do
        # Get everything after the last '/'
        filename="${line##*/}"

        # Strip everything after '?'
        stripped_query_params="${filename%%\?*}"

        curl -f -b "$cookiejar" -c "$cookiejar" -L --netrc-file "$netrc" -g -o $stripped_query_params -- $line && echo || exit_with_error "Command failed with error. Please retrieve the data manually."
      done;
  elif command -v wget >/dev/null 2>&1; then
      # We can't use wget to poke provider server to get info whether or not URS was integrated without download at least one of the files.
      echo
      echo "WARNING: Can't find curl, use wget instead."
      echo "WARNING: Script may not correctly identify Earthdata Login integrations."
      echo
      setup_auth_wget
      while read -r line; do
        # Get everything after the last '/'
        filename="${line##*/}"

        # Strip everything after '?'
        stripped_query_params="${filename%%\?*}"

        wget --load-cookies "$cookiejar" --save-cookies "$cookiejar" --output-document $stripped_query_params --keep-session-cookies -- $line && echo || exit_with_error "Command failed with error. Please retrieve the data manually."
      done;
  else
      exit_with_error "Error: Could not find a command-line downloader.  Please install curl or wget"
  fi
}

fetch_urls <<'EDSCEOF'
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107234251_08052501_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107232206_08042512_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107230842_08042510_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107230240_08042509_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107225537_08042508_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107224836_08042507_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107224005_08042506_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107223440_08042505_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107222931_08042504_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107222406_08042503_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107220834_08042501_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107220132_08032514_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107215530_08032513_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107214749_08032512_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107213425_08032510_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107212823_08032509_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107211418_08032507_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107210548_08032506_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107210023_08032505_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107204949_08032503_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107204119_08032502_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107202715_08022514_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107202113_08022513_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107201332_08022512_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107200008_08022510_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107193131_08022506_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107192606_08022505_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107192057_08022504_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107191532_08022503_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107190702_08022502_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107190000_08022501_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107185258_08012514_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107184656_08012513_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107183915_08012512_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107182551_08012510_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107175714_08012506_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107174115_08012503_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107173245_08012502_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107171841_08002514_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107170458_08002512_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107165134_08002510_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107163829_08002508_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107162257_08002506_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107161732_08002505_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107160658_08002503_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107155828_08002502_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107154424_07992514_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107153041_07992512_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107151717_07992510_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107151115_07992509_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107150412_07992508_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107145710_07992507_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107144315_07992505_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107143806_07992504_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107143241_07992503_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107140405_07982513_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107135624_07982512_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107134300_07982510_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107132955_07982508_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107132253_07982507_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107130858_07982505_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107130349_07982504_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107125824_07982503_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107124252_07982501_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107123549_07972514_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107122948_07972513_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107122207_07972512_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107120843_07972510_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107114836_07972507_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107113441_07972505_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107112932_07972504_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107112407_07972503_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107111536_07972502_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107110834_07972501_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107110132_07962514_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107105530_07962513_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107104749_07962512_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107103425_07962510_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107102121_07962508_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107101419_07962507_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107100024_07962505_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107094950_07962503_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107094119_07962502_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107092113_07952513_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107091332_07952512_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107090008_07952510_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107085406_07952509_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107084704_07952508_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107084002_07952507_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107083132_07952506_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107082607_07952505_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107082058_07952504_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107081533_07952503_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107073915_07942512_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107072551_07942510_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107071247_07942508_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107065715_07942506_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107065150_07942505_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107064641_07942504_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107064115_07942503_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107063245_07942502_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107062543_07942501_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107061239_07932513_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107060458_07932512_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107055134_07932510_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107054532_07932509_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107053830_07932508_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107053128_07932507_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107052258_07932506_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107051733_07932505_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107050658_07932503_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107045828_07932502_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107043822_07922513_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107043041_07922512_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107041717_07922510_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107040413_07922508_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107034316_07922505_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107033241_07922503_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107032411_07922502_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107031709_07922501_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107031007_07912514_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107030405_07912513_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107025624_07912512_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107024300_07912510_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107022956_07912508_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107020859_07912505_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107015824_07912503_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107013550_07902514_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107012207_07902512_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107010843_07902510_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107004837_07902507_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107003441_07902505_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107002932_07902504_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107002407_07902503_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241107000835_07902501_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/07/ATL24_20241106235531_07892513_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/06/ATL24_20241106234750_07892512_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/06/ATL24_20241106233426_07892510_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/06/ATL24_20241106232121_07892508_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/06/ATL24_20241106231420_07892507_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/06/ATL24_20241106230549_07892506_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/06/ATL24_20241106230024_07892505_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/06/ATL24_20241106225515_07892504_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/06/ATL24_20241106224950_07892503_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/06/ATL24_20241106223418_07892501_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/06/ATL24_20241106222715_07882514_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/06/ATL24_20241106221333_07882512_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/06/ATL24_20241106220009_07882510_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/06/ATL24_20241106215407_07882509_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/06/ATL24_20241106214002_07882507_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/06/ATL24_20241106213132_07882506_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/06/ATL24_20241106212607_07882505_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/06/ATL24_20241106212058_07882504_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/06/ATL24_20241106211533_07882503_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/06/ATL24_20241106210703_07882502_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/06/ATL24_20241106210001_07882501_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/06/ATL24_20241106205258_07872514_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/06/ATL24_20241106204656_07872513_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/06/ATL24_20241106203916_07872512_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/06/ATL24_20241106202552_07872510_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/06/ATL24_20241106201247_07872508_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/06/ATL24_20241106195715_07872506_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/06/ATL24_20241106195150_07872505_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/06/ATL24_20241106194641_07872504_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/06/ATL24_20241106194116_07872503_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/06/ATL24_20241106193245_07872502_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/06/ATL24_20241106192543_07872501_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/06/ATL24_20241106191841_07862514_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/06/ATL24_20241106190459_07862512_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/06/ATL24_20241106185135_07862510_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/06/ATL24_20241106183128_07862507_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/06/ATL24_20241106182258_07862506_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/06/ATL24_20241106181733_07862505_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/06/ATL24_20241106180659_07862503_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/06/ATL24_20241106175828_07862502_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/06/ATL24_20241106174424_07852514_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/06/ATL24_20241106173822_07852513_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/06/ATL24_20241106173041_07852512_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/06/ATL24_20241106172458_07852511_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/06/ATL24_20241106171717_07852510_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/06/ATL24_20241106170413_07852508_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/06/ATL24_20241106164841_07852506_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/06/ATL24_20241106164316_07852505_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/06/ATL24_20241106163807_07852504_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/06/ATL24_20241106163242_07852503_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/06/ATL24_20241106162411_07852502_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/06/ATL24_20241106161709_07852501_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/06/ATL24_20241106155624_07842512_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/06/ATL24_20241106154300_07842510_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/06/ATL24_20241106153658_07842509_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/06/ATL24_20241106152254_07842507_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/06/ATL24_20241106150859_07842505_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/06/ATL24_20241106150349_07842504_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/06/ATL24_20241106145824_07842503_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/06/ATL24_20241106144954_07842502_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/06/ATL24_20241106142207_07832512_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/06/ATL24_20241106140843_07832510_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/06/ATL24_20241106135539_07832508_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/06/ATL24_20241106134837_07832507_006_01_001_01.h5
https://data.nsidc.earthdatacloud.nasa.gov/nsidc-cumulus-prod-protected/ATLAS/ATL24/001/2024/11/06/ATL24_20241106133441_07832505_006_01_001_01.h5
EDSCEOF
