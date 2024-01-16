# -*- coding: utf-8 -*-
#
import re

from aqt import mw
from aqt.qt import *

from .utils import JS_DIR
from .config import Config
from .user_messages import info_window


class CSSJSHandler:
    def __init__(self):
        self.wrapperDict = False
        self.chineseParserHeader = "<!--###MIGAKU CHINESE SUPPORT JS START###\nDo Not Edit If Using Automatic CSS and JS Management-->"
        self.chineseParserFooter = "<!--###MIGAKU CHINESE SUPPORT JS ENDS###-->"
        self.chineseCSSHeader = "/*###MIGAKU CHINESE SUPPORT CSS STARTS###\nDo Not Edit If Using Automatic CSS and JS Management*/"
        self.chineseCSSFooter = "/*###MIGAKU CHINESE SUPPORT CSS ENDS###*/"
        self.chineseCSSPattern = "\/\*###MIGAKU CHINESE SUPPORT CSS STARTS###\nDo Not Edit If Using Automatic CSS and JS Management\*\/[^*]*?\/\*###MIGAKU CHINESE SUPPORT CSS ENDS###\*\/"

        self.chineseParserJS = self.getCParser()

    def updateWrapperDict(self):
        self.wrapperDict, wrapperCheck = self.getWrapperDict()

    def getCParser(self):
        chineseParser = JS_DIR / "chineseparser.js"
        with chineseParser.open("r", encoding="utf-8") as chineseParserFile:
            return chineseParserFile.read()

    def noteCardFieldExists(self, data):
        models = mw.col.models.all()
        error = ""
        note = False
        card = False
        field = False
        side = False
        if data[5] in ["both", "front", "back"]:
            side = True
        for model in models:
            if model["name"] == data[2] and not note:
                note = True
                for t in model["tmpls"]:
                    if t["name"] == data[3] and not card:
                        card = True
                for fld in model["flds"]:
                    if fld["name"] == data[4] and not field:
                        field = True
        if not note:
            return (
                False,
                'The "'
                + data[2]
                + '" note type does not exist in this profile, if this note type exists in another profile consider setting its profile setting to the appropriate profile in the Active Fields settings menu.',
            )

        if not card:
            error += 'The "' + data[3] + '" card type does not exist.\n'
        if not field:
            error += 'The "' + data[4] + '" field does not exist.\n'
        if not side:
            error += 'The last value must be "front", "back", or "both", it cannot be "' + data[5] + '"'

        if error == "":
            return True, False
        return False, error

    def fieldConflictCheck(self, item, array, dType):
        conflicts = []
        for value in array:
            valAr = value[0]
            valDType = value[1]
            if valAr == item:
                conflicts.append('In "' + valDType + '": ' + ";".join(valAr))
                conflicts.append('In "' + dType + '": ' + ";".join(item))
                return False, conflicts
            elif valAr[2] == item[2] and valAr[3] == item[3] and valAr[4] == item[4] and (valAr[5] == "both" or item[5] == "both"):
                conflicts.append('In "' + valDType + '": ' + ";".join(valAr))
                conflicts.append('In "' + dType + '": ' + ";".join(item))
                return False, conflicts
        return True, True

    def getWrapperDict(self):
        wrapperDict = {}
        displayOptions = [
            "hover",
            "coloredhover",
            "hanzi",
            "coloredhanzi",
            "reading",
            "coloredreading",
            "hanzireading",
            "coloredhanzireading",
        ]
        syntaxErrors = ""
        notFoundErrors = ""
        fieldConflictErrors = ""
        displayTypeError = ""
        alreadyIncluded = []
        for item in Config.active_fields:
            dataArray = item.split(";")
            displayOption = dataArray[0]
            if (len(dataArray) != 6 and len(dataArray) != 7) or "" in dataArray:
                syntaxErrors += '\n"' + item + '" in "' + displayOption + '"\n'
            elif displayOption.lower() not in displayOptions:
                displayTypeError += '\n"' + item + '" in "ActiveFields" has an incorrect display type of "' + displayOption + '"\n'
            else:
                if mw.pm.name != dataArray[1] and "all" != dataArray[1].lower():
                    continue
                if len(dataArray) == 7:
                    if dataArray[6].lower() not in ["pinyin", "bopomofo", "jyutping"]:
                        syntaxErrors += (
                            '\n"'
                            + item
                            + '" in "ActiveFields"\nThe value "'
                            + dataArray[6]
                            + '" is not valid. The "ReadingType" value must be either "pinyin", "bopomofo", or "jyutping". The default value has been applied.'
                        )
                        dataArray[6] = "default"
                else:
                    dataArray.append("default")
                if dataArray[2] != "noteTypeName" and dataArray[3] != "cardTypeName" and dataArray[4] != "fieldName":
                    success, errorMsg = self.noteCardFieldExists(dataArray)
                    if success:
                        conflictFree, conflicts = self.fieldConflictCheck(dataArray, alreadyIncluded, displayOption)
                        if conflictFree:
                            if dataArray[2] not in wrapperDict:
                                alreadyIncluded.append([dataArray, displayOption])
                                wrapperDict[dataArray[2]] = [[dataArray[3], dataArray[4], dataArray[5], displayOption, dataArray[6]]]
                            else:
                                if [dataArray[3], dataArray[4], dataArray[5], displayOption, dataArray[6]] not in wrapperDict[dataArray[2]]:
                                    alreadyIncluded.append([dataArray, displayOption])
                                    wrapperDict[dataArray[2]].append(
                                        [dataArray[3], dataArray[4], dataArray[5], displayOption, dataArray[6]]
                                    )
                        else:
                            fieldConflictErrors += "A conflict was found in this field pair:\n\n" + "\n".join(conflicts) + "\n\n"
                    else:
                        notFoundErrors += '"' + item + '" in "ActiveFields" has the following error(s):\n' + errorMsg + "\n\n"

        if syntaxErrors != "":
            info_window(
                'The following entries have incorrect syntax:\nPlease make sure the format is as follows:\n"displayType;profileName;noteTypeName;cardTypeName;fieldName;side(;ReadingType)".\n'
                + syntaxErrors,
                level="err",
            )
            return (wrapperDict, False)
        if displayTypeError != "":
            info_window(
                'The following entries have an incorrect display type. Valid display types are "Hover", "ColoredHover", "Hanzi", "ColoredHanzi", "HanziReading", "ColoredHanziReading", "Reading", and "ColoredReading".\n'
                + syntaxErrors,
                level="err",
            )
            return (wrapperDict, False)
        if fieldConflictErrors != "":
            info_window(
                "You have entries that point to the same field and the same side. Please make sure that a field and side combination does not conflict.\n\n"
                + fieldConflictErrors,
                level="err",
            )
            return (wrapperDict, False)
        return (wrapperDict, True)

    def checkProfile(self):
        if mw.pm.name in Config.profiles or ("all" in Config.profiles or "All" in Config.profiles):
            return True
        return False

    def injectWrapperElements(self):
        if not self.checkProfile():
            return
        if not Config.auto_generate_css_js:
            return
        self.wrapperDict, wrapperCheck = self.getWrapperDict()
        models = mw.col.models.all()
        for model in models:
            if model["name"] in self.wrapperDict:
                model["css"] = self.editChineseCss(model["css"])
                for idx, t in enumerate(model["tmpls"]):
                    modelDict = self.wrapperDict[model["name"]]
                    if self.templateInModelDict(t["name"], modelDict):
                        templateDict = self.templateFilteredDict(modelDict, t["name"])
                        t["qfmt"], t["afmt"] = self.cleanFieldWrappers(t["qfmt"], t["afmt"], model["flds"], templateDict)
                        for data in templateDict:
                            if data[2] == "both" or data[2] == "front":
                                t["qfmt"] = self.overwriteWrapperElement(t["qfmt"], data[1], data[3], data[4])
                                t["qfmt"] = self.injectWrapperElement(t["qfmt"], data[1], data[3], data[4])
                                t["qfmt"] = self.editChineseJs(t["qfmt"])
                            if data[2] == "both" or data[2] == "back":
                                t["afmt"] = self.overwriteWrapperElement(t["afmt"], data[1], data[3], data[4])
                                t["afmt"] = self.injectWrapperElement(t["afmt"], data[1], data[3], data[4])
                                t["afmt"] = self.editChineseJs(t["afmt"])
                    else:
                        t["qfmt"] = self.removeWrappers(t["qfmt"])
                        t["afmt"] = self.removeWrappers(t["afmt"])

            else:
                model["css"] = self.removeChineseCss(model["css"])
                for t in model["tmpls"]:
                    t["qfmt"] = self.removeChineseJs(self.removeWrappers(t["qfmt"]))
                    t["afmt"] = self.removeChineseJs(self.removeWrappers(t["afmt"]))
            mw.col.models.save(model)
        return wrapperCheck

    def checkReadingType(self):
        rType = Config.reading_type
        if rType not in ["pinyin", "bopomofo", "jyutping"]:
            info_window(
                'The "'
                + rType
                + '" value in the "ReadingType" configuration is incorrect. The value must be "pinyin", "bopomofo", or "jyutping".',
                level="err",
            )
            return False
        return True

    def newLineReduce(self, text):
        return re.sub(r"\n{3,}", "\n\n", text)

    def getRubyFontSize(self):
        return ".pinyin-ruby{font-size:" + str(Config.ruby_font_scale_factor) + "% !important;}"

    def getChineseCss(self):
        toneColors = Config.mandarin_tones
        css = (
            ".nightMode .unhovered-word .hanzi-ruby{color:white !important;}.unhovered-word .hanzi-ruby{color:inherit !important;}.unhovered-word .pinyin-ruby{visibility:hidden  !important;}"
            + self.getRubyFontSize()
        )
        count = 1
        for toneColor in toneColors:
            css += ".tone%s{color:%s;}.ankidroid_dark_mode .tone%s, .nightMode .tone%s{color:%s;}" % (
                str(count),
                toneColor,
                str(count),
                str(count),
                toneColor,
            )
            count += 1
        toneColors = Config.cantonese_tones
        count = 1
        for toneColor in toneColors:
            css += ".canTone%s{color:%s;}.ankidroid_dark_mode .canTone%s, .nightMode .cantone%s{color:%s;}" % (
                str(count),
                toneColor,
                str(count),
                str(count),
                toneColor,
            )
            count += 1
        return self.chineseCSSHeader + "\n" + css + "\n" + self.chineseCSSFooter

    def editChineseCss(self, css: str):
        pattern = self.chineseCSSPattern
        chineseCss = self.getChineseCss()
        if not css:
            return chineseCss
        match = re.search(pattern, css)
        if match:
            if match.group() != chineseCss:
                return css.replace(match.group(), chineseCss)
            else:
                return css
        else:
            return css + "\n" + chineseCss

    def templateInModelDict(self, template, modelDict):
        for entries in modelDict:
            if entries[0] == template:
                return True
        return False

    def templateFilteredDict(self, modelDict, template):
        return list(filter(lambda data, tname=template: data[0] == tname, modelDict))

    def fieldInTemplateDict(self, field, templateDict):
        sides = []
        for entries in templateDict:
            if entries[1] == field:
                sides.append(entries[2])
        return sides

    def removeChineseJs(self, text):
        return re.sub(self.chineseParserHeader + r".*?" + self.chineseParserFooter, "", text)

    def cleanFieldWrappers(self, front, back, fields, templateDict):
        for field in fields:
            sides = self.fieldInTemplateDict(field["name"], templateDict)

            if len(sides) > 0:
                pattern = r'<div reading-type="[^>]+?" display-type="[^>]+?" class="wrapped-chinese">({{' + field["name"] + "}})</div>"
                if "both" not in sides or "front" not in sides:
                    front = re.sub(pattern, "{{" + field["name"] + "}}", front)
                    front = self.removeChineseJs(front)
                if "both" not in sides or "back" not in sides:
                    back = re.sub(pattern, "{{" + field["name"] + "}}", back)
                    back = self.removeChineseJs(back)
            else:
                pattern = r'<div reading-type="[^>]+?" display-type="[^>]+?" class="wrapped-chinese">({{' + field["name"] + "}})</div>"
                front = re.sub(pattern, "{{" + field["name"] + "}}", front)
                back = re.sub(pattern, "{{" + field["name"] + "}}", back)
                front = self.removeChineseJs(front)
                back = self.removeChineseJs(back)
        return front, back

    def overwriteWrapperElement(self, text, field, dType, rType="default"):
        pattern = r'<div reading-type="([^>]+?)" display-type="([^>]+?)" class="wrapped-chinese">{{' + field + r"}}</div>"
        finds = re.findall(pattern, text)

        if len(finds) > 0:
            for find in finds:
                if dType.lower() != find[1].lower() or rType.lower() != find[0].lower():
                    toReplace = (
                        '<div reading-type="'
                        + find[0]
                        + '" display-type="'
                        + find[1]
                        + '" class="wrapped-chinese">{{'
                        + field
                        + r"}}</div>"
                    )
                    replaceWith = (
                        '<div reading-type="' + rType + '" display-type="' + dType + '" class="wrapped-chinese">{{' + field + r"}}</div>"
                    )
                    text = text.replace(toReplace, replaceWith)

        return text

    def injectWrapperElement(self, text, field, dType, rType="default"):
        pattern = r'(?<!(?:class="wrapped-chinese">))({{' + field + r"}})"
        replaceWith = '<div reading-type="' + rType + '" display-type="' + dType + '" class="wrapped-chinese">{{' + field + "}}</div>"
        text = re.sub(pattern, replaceWith, text)
        return text

    def getChineseJs(self):
        js = '<script>(function(){const CHINESE_READING_TYPE ="' + Config.reading_type + '";' + self.chineseParserJS + "})();</script>"
        return self.chineseParserHeader + js + self.chineseParserFooter

    def editChineseJs(self, text):
        pattern = self.chineseParserHeader + r".*?" + self.chineseParserFooter
        chineseJS = self.getChineseJs()
        if not text:
            return chineseJS
        match = re.search(pattern, text)
        if match:
            if match.group() != chineseJS:
                return self.newLineReduce(re.sub(match.group, chineseJS, text))
            else:
                return text
        else:
            return self.newLineReduce(text + "\n" + chineseJS)

    def removeWrappers(self, text):
        pattern = r'<div reading-type="[^>]+?" display-type="[^>]+?" class="wrapped-chinese">({{[^}]+?}})</div>'
        text = re.sub(pattern, r"\1", text)
        return text

    def removeChineseCss(self, css):
        return re.sub(self.chineseCSSPattern, "", css)
