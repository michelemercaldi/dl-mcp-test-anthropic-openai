# Visual Diagram for WebDAV Server Setup

## Diagram

```plaintext
1. Create ASP.NET Core Project
   └── Select WebAPI Template

2. Configure NuGet Repository  (optional)
   └── Add WebDAV Source

3. Install WebDAV Packages
   ├── FubarDev.WebDavServer
   ├── FubarDev.WebDavServer.FileSystem.DotNet
   ├── FubarDev.WebDavServer.Props.Store.TextFile
   ├── FubarDev.WebDavServer.Locking.InMemory
   └── FubarDev.WebDavServer.AspNetCore

4. Create WebDAV Controller
   └── Rename and Modify Code

5. Configure Services (Startup.cs)
   ├── Set FileSystem Options
   ├── Add Required Services
   └── Use AddMvcCore

6. Add NTLM Authentication
   ├── Add Authentication Package
   ├── Authorize Controller
   └── Modify Program.cs

7. Disable Automatic Browser Launch
   └── Edit launchSettings.json

8. Change Start Project
   └── From IIS Express to TestWebDavServer

9. Run Test Server
   └── Connect using WebDAV URL
```