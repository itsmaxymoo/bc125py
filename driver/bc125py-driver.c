/* setuid driver setup helper for bc125at-perl */

/*
* Copyright (c) 2013, Rikus Goodell.
* 
* All rights reserved.
* 
* Permission is hereby granted, free of charge, to any person obtaining a
* copy of this software and associated documentation files (the "Software"),
* to deal in the Software without restriction, including without limitation
* the rights to use, copy, modify, merge, publish, distribute, sublicense,
* and/or sell copies of the Software, and to permit persons to whom the
* Software is furnished to do so, subject to the following conditions:
* 
* The above copyright notice and this permission notice shall be included
* in all copies or substantial portions of the Software.
* 
* THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
* IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
* FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
* THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
* OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
* ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
* OTHER DEALINGS IN THE SOFTWARE.
*/

/* Lines 51-54 Copyright (c) 2022 Max Loiacono, MIT License */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <sys/types.h>
#include <unistd.h>

#define LINEBUF_MAX 4096
#define ID_MAX 16

void extract_value(char *, char *, char *);
int setup_device(char *, char *);

int main (int argc, char *argv[]){
	FILE *usbdev;
	char linebuf[LINEBUF_MAX];
	char vendor[ID_MAX], product[ID_MAX];
	char found_device;

	vendor[0]	= 0;
	product[0]   = 0;
	found_device = 0;

	/* Find the correct usb list file */
	if( (usbdev = fopen("/proc/bus/usb/devices", "r")) ){}
	else if ( (usbdev = fopen("/sys/kernel/debug/usb/devices", "r")) ) {}
	else { return 1; }


	while( fgets(linebuf, LINEBUF_MAX, usbdev) ){
		if(strstr(linebuf, "BC125AT")){
			found_device   = 1;
		}
		else if(!linebuf[0] || !(linebuf[0] >= 'A' && linebuf[0] <= 'Z')){
			vendor[0]  = 0;
			product[0] = 0;
		}

		if(found_device && vendor[0] && product[0]) break;

		extract_value( linebuf, "Vendor=", vendor  );
		extract_value( linebuf, "ProdID=", product );
	}
	
	if (!found_device){
		printf("found_device=%d\n", found_device);
		return 1;
	}

	printf("found_device=%d; vendor=%s; product=%s\n", found_device, vendor, product);
	
	return setup_device(vendor, product);
}

void extract_value(char *linebuf, char *match, char *result){
	char *where;
	short int pos;
	where = strstr(linebuf, match);
	if (where){
		where += strlen(match);
		for (pos = 0; pos < ID_MAX && *(where + pos) != 0 && *(where + pos) != ' '; pos++){
			*(result + pos) = *(where + pos);
		}
		*(result + pos) = 0;
	}
}

int setup_device(char *vendor, char *product){
	uid_t orig_uid, orig_gid;
	
	orig_uid = getuid();
	orig_gid = getgid();

	setuid(0);

	if (getuid() != 0){
		printf("Couldn't setuid to 0\n");
		return 1;
	}
	else {
		system("echo 1965 0017 2 076d 0006 > /sys/bus/usb/drivers/cdc_acm/new_id");
		usleep(250 * 1000); /* sleep 250 ms before chown or, oddly, it may not take effect */
		if (chown("/dev/ttyACM0", orig_uid, orig_gid) == -1)
			perror("chown failed");
	}
	return 0;
}
