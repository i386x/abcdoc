/**
 * \file    ./static/js/doitdoc.js
 * \author  Jiří Kučera, <sanczes AT gmail.com>
 * \stamp   2018-05-05 11:45:06 (UTC+0100, DST+0100)
 * \project DoIt! Doc: Sphinx Template for DoIt! Documentation
 * \license MIT
 * \version 0.0.0
 * \brief   DoIt! Doc utilities.
 */
;(function (window) {
    "use strict";

    var global = window || this,
        document = window && window.document;

    if (!document) {
        throw new Error("window has no document!");
    }

    if (global.$dd) {
        return;
    }

    global.$dd = {};

    function halt() {
        throw new Error("halted");
    }

    function dshow(s) {
        alert(s);
        halt();
    }

    function show_elms(cls, a, b) {
        var s = "",
            elms = document.getElementsByClassName(cls);

        if (!elms) {
            dshow("There are no elements with '" + cls + "' class.");
        }
        a = a || 0;
        b = b || elms.length;
        if (a < 0 || b < 0 || a >= b) {
            dshow("Invalid range [" + a + ", " + b + ")\n");
        }
        s = s + "# of elms: " + elms.length + "\n";
        for (var i = 0; i < elms.length; i++) {
            if (i < a || b <= i) {
                continue;
            }
            s = s + "Properties of '" + elms[i] + "':\n";
            for (var p in elms[i]) {
                s += "- " + p + "\n";
            }
        }
        dshow(s);
    }

    $dd.each = function (a, f) {
        for (var i = 0; i < a.length; i++) {
            f(a[i]);
        }
    };

    $dd.w = $dd.width = function (id) {
        var e = document.getElementById(id);

        return e && e.offsetWidth || 0;
    };

    $dd.h = $dd.height = function (id) {
        var e = document.getElementById(id);

        return e && e.offsetHeight || 0;
    };

    $dd.dimen = function (id, prop, x) {
        var e = document.getElementById(id);

        if (e && e.style) {
            e.style[prop] = x + "px";
        }
    };

    $dd.style = function (e, s) {
        for (var p in s) {
            e.style[p] = s[p];
        }
    };

    $dd.elms = function (cls) {
        return document.getElementsByClassName(cls) || [];
    };

    $dd.toc = function (name, indent) {
        var prefix = "toc" + name,
            toc_i_id = prefix + "-i",
            toc_ii_id = prefix + "-ii",
            toc_iii_id = prefix + "-iii",
            mb_i_id = prefix + "-mb-i",
            mb_ii_id = prefix + "-mb-ii",
            lab_i_cls = prefix + "-lab-i",
            lab_ii_cls = prefix + "-lab-ii",
            w_i = $dd.w(mb_i_id),
            w_ii = $dd.w(mb_ii_id),
            makestyle = function (x) {
                if (x <= 0) {
                    return {};
                }
                return { "width": x + "px", "float": "left" };
            };

        $dd.dimen(toc_i_id, "padding-left", indent);
        $dd.each($dd.elms(lab_i_cls), function (e) {
            $dd.style(e, makestyle(w_i));
        });
        $dd.dimen(toc_ii_id, "padding-left", w_i);
        $dd.each($dd.elms(lab_ii_cls), function (e) {
            $dd.style(e, makestyle(w_ii));
        });
        $dd.dimen(toc_iii_id, "padding-left", w_ii);
    };
})(typeof window === "undefined" ? this : window);
