/* GLIB - Library of useful routines for C programming
 * Copyright (C) 1995-1997  Peter Mattis, Spencer Kimball and Josh MacDonald
 *
 * SPDX-License-Identifier: LGPL-2.1-or-later
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2.1 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, see <http://www.gnu.org/licenses/>.
 */

/*
 * Modified by the GLib Team and others 1997-2000.  See the AUTHORS
 * file for a list of people on the GLib Team.  See the ChangeLog
 * files for a list of changes.  These files are distributed with
 * GLib at ftp://ftp.gtk.org/pub/gtk/.
 */

/*
 * MT safe
 */

//#include "config.h"

#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <locale.h>
#include <string.h>
#include <locale.h>
#include <errno.h>
//#include <garray.h>
#include <ctype.h>              /* For tolower() */

#ifdef HAVE_XLOCALE_H
/* Needed on BSD/OS X for e.g. strtod_l */
#include <xlocale.h>
#endif

#ifdef G_OS_WIN32
#include <windows.h>
#endif

/* do not include <unistd.h> here, it may interfere with g_strsignal() */

#include "gstrfuncs.h"

//#include "gprintf.h"
//#include "gprintfint.h"
//#include "glibintl.h"


/**
 * SECTION:string_utils
 * @title: String Utility Functions
 * @short_description: various string-related functions
 *
 * This section describes a number of utility functions for creating,
 * duplicating, and manipulating strings.
 *
 * Note that the functions g_printf(), g_fprintf(), g_sprintf(),
 * g_vprintf(), g_vfprintf(), g_vsprintf() and g_vasprintf()
 * are declared in the header `gprintf.h` which is not included in `glib.h`
 * (otherwise using `glib.h` would drag in `stdio.h`), so you'll have to
 * explicitly include `<glib/gprintf.h>` in order to use the GLib
 * printf() functions.
 *
 * ## String precision pitfalls # {#string-precision}
 *
 * While you may use the printf() functions to format UTF-8 strings,
 * notice that the precision of a \%Ns parameter is interpreted
 * as the number of bytes, not characters to print. On top of that,
 * the GNU libc implementation of the printf() functions has the
 * "feature" that it checks that the string given for the \%Ns
 * parameter consists of a whole number of characters in the current
 * encoding. So, unless you are sure you are always going to be in an
 * UTF-8 locale or your know your text is restricted to ASCII, avoid
 * using \%Ns. If your intention is to format strings for a
 * certain number of columns, then \%Ns is not a correct solution
 * anyway, since it fails to take wide characters (see g_unichar_iswide())
 * into account.
 *
 * Note also that there are various printf() parameters which are platform
 * dependent. GLib provides platform independent macros for these parameters
 * which should be used instead. A common example is %G_GUINT64_FORMAT, which
 * should be used instead of `%llu` or similar parameters for formatting
 * 64-bit integers. These macros are all named `G_*_FORMAT`; see
 * [Basic Types][glib-Basic-Types].
 */

/**
 * g_ascii_isalnum:
 * @c: any character
 *
 * Determines whether a character is alphanumeric.
 *
 * Unlike the standard C library isalnum() function, this only
 * recognizes standard ASCII letters and ignores the locale,
 * returning %FALSE for all non-ASCII characters. Also, unlike
 * the standard library function, this takes a char, not an int,
 * so don't call it on %EOF, but no need to cast to #guchar before
 * passing a possibly non-ASCII character in.
 *
 * Returns: %TRUE if @c is an ASCII alphanumeric character
 */

/**
 * g_ascii_isalpha:
 * @c: any character
 *
 * Determines whether a character is alphabetic (i.e. a letter).
 *
 * Unlike the standard C library isalpha() function, this only
 * recognizes standard ASCII letters and ignores the locale,
 * returning %FALSE for all non-ASCII characters. Also, unlike
 * the standard library function, this takes a char, not an int,
 * so don't call it on %EOF, but no need to cast to #guchar before
 * passing a possibly non-ASCII character in.
 *
 * Returns: %TRUE if @c is an ASCII alphabetic character
 */

/**
 * g_ascii_iscntrl:
 * @c: any character
 *
 * Determines whether a character is a control character.
 *
 * Unlike the standard C library iscntrl() function, this only
 * recognizes standard ASCII control characters and ignores the
 * locale, returning %FALSE for all non-ASCII characters. Also,
 * unlike the standard library function, this takes a char, not
 * an int, so don't call it on %EOF, but no need to cast to #guchar
 * before passing a possibly non-ASCII character in.
 *
 * Returns: %TRUE if @c is an ASCII control character.
 */

/**
 * g_ascii_isdigit:
 * @c: any character
 *
 * Determines whether a character is digit (0-9).
 *
 * Unlike the standard C library isdigit() function, this takes
 * a char, not an int, so don't call it  on %EOF, but no need to
 * cast to #guchar before passing a possibly non-ASCII character in.
 *
 * Returns: %TRUE if @c is an ASCII digit.
 */

/**
 * g_ascii_isgraph:
 * @c: any character
 *
 * Determines whether a character is a printing character and not a space.
 *
 * Unlike the standard C library isgraph() function, this only
 * recognizes standard ASCII characters and ignores the locale,
 * returning %FALSE for all non-ASCII characters. Also, unlike
 * the standard library function, this takes a char, not an int,
 * so don't call it on %EOF, but no need to cast to #guchar before
 * passing a possibly non-ASCII character in.
 *
 * Returns: %TRUE if @c is an ASCII printing character other than space.
 */

/**
 * g_ascii_islower:
 * @c: any character
 *
 * Determines whether a character is an ASCII lower case letter.
 *
 * Unlike the standard C library islower() function, this only
 * recognizes standard ASCII letters and ignores the locale,
 * returning %FALSE for all non-ASCII characters. Also, unlike
 * the standard library function, this takes a char, not an int,
 * so don't call it on %EOF, but no need to worry about casting
 * to #guchar before passing a possibly non-ASCII character in.
 *
 * Returns: %TRUE if @c is an ASCII lower case letter
 */

/**
 * g_ascii_isprint:
 * @c: any character
 *
 * Determines whether a character is a printing character.
 *
 * Unlike the standard C library isprint() function, this only
 * recognizes standard ASCII characters and ignores the locale,
 * returning %FALSE for all non-ASCII characters. Also, unlike
 * the standard library function, this takes a char, not an int,
 * so don't call it on %EOF, but no need to cast to #guchar before
 * passing a possibly non-ASCII character in.
 *
 * Returns: %TRUE if @c is an ASCII printing character.
 */

/**
 * g_ascii_ispunct:
 * @c: any character
 *
 * Determines whether a character is a punctuation character.
 *
 * Unlike the standard C library ispunct() function, this only
 * recognizes standard ASCII letters and ignores the locale,
 * returning %FALSE for all non-ASCII characters. Also, unlike
 * the standard library function, this takes a char, not an int,
 * so don't call it on %EOF, but no need to cast to #guchar before
 * passing a possibly non-ASCII character in.
 *
 * Returns: %TRUE if @c is an ASCII punctuation character.
 */

/**
 * g_ascii_isspace:
 * @c: any character
 *
 * Determines whether a character is a white-space character.
 *
 * Unlike the standard C library isspace() function, this only
 * recognizes standard ASCII white-space and ignores the locale,
 * returning %FALSE for all non-ASCII characters. Also, unlike
 * the standard library function, this takes a char, not an int,
 * so don't call it on %EOF, but no need to cast to #guchar before
 * passing a possibly non-ASCII character in.
 *
 * Returns: %TRUE if @c is an ASCII white-space character
 */

/**
 * g_ascii_isupper:
 * @c: any character
 *
 * Determines whether a character is an ASCII upper case letter.
 *
 * Unlike the standard C library isupper() function, this only
 * recognizes standard ASCII letters and ignores the locale,
 * returning %FALSE for all non-ASCII characters. Also, unlike
 * the standard library function, this takes a char, not an int,
 * so don't call it on %EOF, but no need to worry about casting
 * to #guchar before passing a possibly non-ASCII character in.
 *
 * Returns: %TRUE if @c is an ASCII upper case letter
 */

/**
 * g_ascii_isxdigit:
 * @c: any character
 *
 * Determines whether a character is a hexadecimal-digit character.
 *
 * Unlike the standard C library isxdigit() function, this takes
 * a char, not an int, so don't call it on %EOF, but no need to
 * cast to #guchar before passing a possibly non-ASCII character in.
 *
 * Returns: %TRUE if @c is an ASCII hexadecimal-digit character.
 */

/**
 * G_ASCII_DTOSTR_BUF_SIZE:
 *
 * A good size for a buffer to be passed into g_ascii_dtostr().
 * It is guaranteed to be enough for all output of that function
 * on systems with 64bit IEEE-compatible doubles.
 *
 * The typical usage would be something like:
 * |[<!-- language="C" -->
 *   char buf[G_ASCII_DTOSTR_BUF_SIZE];
 *
 *   fprintf (out, "value=%s\n", g_ascii_dtostr (buf, sizeof (buf), value));
 * ]|
 */

/**
 * g_strstrip:
 * @string: a string to remove the leading and trailing whitespace from
 *
 * Removes leading and trailing whitespace from a string.
 * See g_strchomp() and g_strchug().
 *
 * Returns: @string
 */

/**
 * G_STR_DELIMITERS:
 *
 * The standard delimiters, used in g_strdelimit().
 */

 static const guint16 ascii_table_data[256] = {
   0x004, 0x004, 0x004, 0x004, 0x004, 0x004, 0x004, 0x004,
   0x004, 0x104, 0x104, 0x004, 0x104, 0x104, 0x004, 0x004,
   0x004, 0x004, 0x004, 0x004, 0x004, 0x004, 0x004, 0x004,
   0x004, 0x004, 0x004, 0x004, 0x004, 0x004, 0x004, 0x004,
   0x140, 0x0d0, 0x0d0, 0x0d0, 0x0d0, 0x0d0, 0x0d0, 0x0d0,
   0x0d0, 0x0d0, 0x0d0, 0x0d0, 0x0d0, 0x0d0, 0x0d0, 0x0d0,
   0x459, 0x459, 0x459, 0x459, 0x459, 0x459, 0x459, 0x459,
   0x459, 0x459, 0x0d0, 0x0d0, 0x0d0, 0x0d0, 0x0d0, 0x0d0,
   0x0d0, 0x653, 0x653, 0x653, 0x653, 0x653, 0x653, 0x253,
   0x253, 0x253, 0x253, 0x253, 0x253, 0x253, 0x253, 0x253,
   0x253, 0x253, 0x253, 0x253, 0x253, 0x253, 0x253, 0x253,
   0x253, 0x253, 0x253, 0x0d0, 0x0d0, 0x0d0, 0x0d0, 0x0d0,
   0x0d0, 0x473, 0x473, 0x473, 0x473, 0x473, 0x473, 0x073,
   0x073, 0x073, 0x073, 0x073, 0x073, 0x073, 0x073, 0x073,
   0x073, 0x073, 0x073, 0x073, 0x073, 0x073, 0x073, 0x073,
   0x073, 0x073, 0x073, 0x0d0, 0x0d0, 0x0d0, 0x0d0, 0x004
   /* the upper 128 are all zeroes */
 };

 const guint16 * const g_ascii_table = ascii_table_data;

 gdouble
 g_ascii_strtod (const gchar *nptr,
                 gchar      **endptr)
 {
 #if defined(USE_XLOCALE) && defined(HAVE_STRTOD_L)

   g_return_val_if_fail (nptr != NULL, 0);

   errno = 0;

   return strtod_l (nptr, endptr, get_C_locale ());

 #else

   gchar *fail_pos;
   gdouble val;
 #ifndef __BIONIC__
   struct lconv *locale_data;
 #endif
   const char *decimal_point;
   gsize decimal_point_len;
   const char *p, *decimal_point_pos;
   const char *end = NULL; /* Silence gcc */
   int strtod_errno;

   g_return_val_if_fail (nptr != NULL, 0);

   fail_pos = NULL;

 #ifndef __BIONIC__
   locale_data = localeconv ();
   decimal_point = locale_data->decimal_point;
   decimal_point_len = strlen (decimal_point);
 #else
   decimal_point = ".";
   decimal_point_len = 1;
 #endif

   g_assert (decimal_point_len != 0);

   decimal_point_pos = NULL;
   end = NULL;

   if (decimal_point[0] != '.' ||
       decimal_point[1] != 0)
     {
       p = nptr;
       /* Skip leading space */
       while (g_ascii_isspace (*p))
         p++;

       /* Skip leading optional sign */
       if (*p == '+' || *p == '-')
         p++;

       if (p[0] == '0' &&
           (p[1] == 'x' || p[1] == 'X'))
         {
           p += 2;
           /* HEX - find the (optional) decimal point */

           while (g_ascii_isxdigit (*p))
             p++;

           if (*p == '.')
             decimal_point_pos = p++;

           while (g_ascii_isxdigit (*p))
             p++;

           if (*p == 'p' || *p == 'P')
             p++;
           if (*p == '+' || *p == '-')
             p++;
           while (g_ascii_isdigit (*p))
             p++;

           end = p;
         }
       else if (g_ascii_isdigit (*p) || *p == '.')
         {
           while (g_ascii_isdigit (*p))
             p++;

           if (*p == '.')
             decimal_point_pos = p++;

           while (g_ascii_isdigit (*p))
             p++;

           if (*p == 'e' || *p == 'E')
             p++;
           if (*p == '+' || *p == '-')
             p++;
           while (g_ascii_isdigit (*p))
             p++;

           end = p;
         }
       /* For the other cases, we need not convert the decimal point */
     }

   if (decimal_point_pos)
     {
       char *copy, *c;

       /* We need to convert the '.' to the locale specific decimal point */
       copy = (char*)g_malloc (end - nptr + 1 + decimal_point_len);

       c = copy;
       memcpy (c, nptr, decimal_point_pos - nptr);
       c += decimal_point_pos - nptr;
       memcpy (c, decimal_point, decimal_point_len);
       c += decimal_point_len;
       memcpy (c, decimal_point_pos + 1, end - (decimal_point_pos + 1));
       c += end - (decimal_point_pos + 1);
       *c = 0;

       errno = 0;
       val = strtod (copy, &fail_pos);
       strtod_errno = errno;

       if (fail_pos)
         {
           if (fail_pos - copy > decimal_point_pos - nptr)
             fail_pos = (char *)nptr + (fail_pos - copy) - (decimal_point_len - 1);
           else
             fail_pos = (char *)nptr + (fail_pos - copy);
         }

       g_free (copy);

     }
   else if (end)
     {
       char *copy;

       copy = (char*)g_malloc (end - (char *)nptr + 1);
       memcpy (copy, nptr, end - nptr);
       *(copy + (end - (char *)nptr)) = 0;

       errno = 0;
       val = strtod (copy, &fail_pos);
       strtod_errno = errno;

       if (fail_pos)
         {
           fail_pos = (char *)nptr + (fail_pos - copy);
         }

       g_free (copy);
     }
   else
     {
       errno = 0;
       val = strtod (nptr, &fail_pos);
       strtod_errno = errno;
     }

   if (endptr)
     *endptr = fail_pos;

   errno = strtod_errno;

   return val;
 #endif
 }

 gchar *
 g_ascii_dtostr (gchar       *buffer,
                 gint         buf_len,
                 gdouble      d)
 {
   return g_ascii_formatd (buffer, buf_len, "%.17g", d);
 }

 gchar *
 g_ascii_formatd (gchar       *buffer,
                  gint         buf_len,
                  const gchar *format,
                  gdouble      d)
 {
 #ifdef USE_XLOCALE
   locale_t old_locale;

   g_return_val_if_fail (buffer != NULL, NULL);
   g_return_val_if_fail (format[0] == '%', NULL);
   g_return_val_if_fail (strpbrk (format + 1, "'l%") == NULL, NULL);

   old_locale = uselocale (get_C_locale ());
    _g_snprintf (buffer, buf_len, format, d);
   uselocale (old_locale);

   return buffer;
 #else
 #ifndef __BIONIC__
   struct lconv *locale_data;
 #endif
   const char *decimal_point;
   gsize decimal_point_len;
   gchar *p;
   int rest_len;
   gchar format_char;

   g_return_val_if_fail (buffer != NULL, NULL);
   g_return_val_if_fail (format[0] == '%', NULL);
   g_return_val_if_fail (strpbrk (format + 1, "'l%") == NULL, NULL);

   format_char = format[strlen (format) - 1];

   g_return_val_if_fail (format_char == 'e' || format_char == 'E' ||
                         format_char == 'f' || format_char == 'F' ||
                         format_char == 'g' || format_char == 'G',
                         NULL);

   if (format[0] != '%')
     return NULL;

   if (strpbrk (format + 1, "'l%"))
     return NULL;

   if (!(format_char == 'e' || format_char == 'E' ||
         format_char == 'f' || format_char == 'F' ||
         format_char == 'g' || format_char == 'G'))
     return NULL;

   _g_snprintf (buffer, buf_len, format, d);

 #ifndef __BIONIC__
   locale_data = localeconv ();
   decimal_point = locale_data->decimal_point;
   decimal_point_len = strlen (decimal_point);
 #else
   decimal_point = ".";
   decimal_point_len = 1;
 #endif

   g_assert (decimal_point_len != 0);

   if (decimal_point[0] != '.' ||
       decimal_point[1] != 0)
     {
       p = buffer;

       while (g_ascii_isspace (*p))
         p++;

       if (*p == '+' || *p == '-')
         p++;

       while (isdigit ((guchar)*p))
         p++;

       if (strncmp (p, decimal_point, decimal_point_len) == 0)
         {
           *p = '.';
           p++;
           if (decimal_point_len > 1)
             {
               rest_len = strlen (p + (decimal_point_len - 1));
               memmove (p, p + (decimal_point_len - 1), rest_len);
               p[rest_len] = 0;
             }
         }
     }

   return buffer;
 #endif
 }
