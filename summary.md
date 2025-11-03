# Getting Started with Your Own WebDAV Server

## Table of Contents
- [Create the basic project](#create-the-basic-project)
- [Configure the WebDAV NuGet repository (optional)](#configure-the-webdav-nuget-repository-optional)
- [Add the WebDAV NuGet packages](#add-the-webdav-nuget-packages)
- [Create the WebDAV controller](#create-the-webdav-controller)
- [Configure the services](#configure-the-services)
- [Add NTLM authentication](#add-ntlm-authentication)
- [Disable the automatic browser launch at application start](#disable-the-automatic-browser-launch-at-application-start)
- [Change the start project (important!)](#change-the-start-project-important)
- [Running the test server](#running-the-test-server)

## You Own WebDAV Server

This walk-through shows how to create your own WebDAV server using Visual Studio 2017.

### Create the basic project
1. Create the ASP.NET Core project.
2. Select the WebAPI template.

### Configure the WebDAV NuGet repository (optional)
1. Open the package manager setup.
2. Add the package source (until release) on MyGet: `https://www.myget.org/F/webdav-server/api/v3/index.json`.

### Add the WebDAV NuGet packages
- **FubarDev.WebDavServer** (WebDAV implementation)
- **FubarDev.WebDavServer.FileSystem.DotNet** (File system implementation)
- **FubarDev.WebDavServer.Props.Store.TextFile** (Stores dead properties in a JSON file)
- **FubarDev.WebDavServer.Locking.InMemory** (In-memory locking implementation)
- **FubarDev.WebDavServer.AspNetCore** (ASP.NET Core and WebDAV glue)

### Create the WebDAV controller
1. Rename `ValuesController.cs` to `WebDavController.cs`.
2. Replace content with the provided code snippet.

### Configure the services
Replace `.AddMvc()` in `Startup.cs` with the appropriate code snippet for configuration.

### Add NTLM authentication
1. Add the `Microsoft.AspNetCore.Authentication` package.
2. Annotate the `WebDavController` with `[Authorize]`.
3. Replace `.UseKestrel()` with `WebListener` settings in `Program.cs`.
4. Remove the IIS integration.

### Disable the automatic browser launch at application start
Modify `launchSettings.json` to set `launchBrowser` to `false`.

### Change the start project (important!)
Change the start project from IIS Express to your test project.

### Running the test server
Start the server and check the WebDAV URL in the console window to connect using Windows Explorer.

---

This summary provides a visual of the steps needed to create a WebDAV server, ensuring a clear and accessible guide for users.