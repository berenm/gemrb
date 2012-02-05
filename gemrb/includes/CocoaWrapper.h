/* GemRB - Infinity Engine Emulator
 * Copyright (C) 2011 The GemRB Project
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
 *
 *
 */

/*
 !!!:
 Because this file is shared between the CocoaWrapper object and plugins extending it we need to keep it
 in the gemrb/includes directory.
*/

#import <Cocoa/Cocoa.h>

#import "exports.h"

extern int GemRB_main(int argc, char *argv[]);

GEM_EXPORT
@interface CocoaWrapper : NSObject
#if __MAC_OS_X_VERSION_MIN_REQUIRED > 1050
<NSApplicationDelegate>
#endif
{
}
// Override these application delegate methods in plugin categories
- (void)applicationWillTerminate:(NSNotification *)aNotification;
- (NSApplicationTerminateReply)applicationShouldTerminate:(NSApplication *)sender;
@end
