# ShortView

A webapp that allows you to create a tracked shortened link and know when it's clicked

# **Try it at [sv.woah.pw](https://sv.woah.pw)**

### What is ShortView?

With this platform, you can shorten a link you want to share with people, and monitor when these links have been opened.
So it allows do do two things at the same time: shorten a long link if you need to, and allow tracking of the link!

### How does this work?

To achieve that, this platform will create a shortened link to the destination url you want to share.
When people will click this link, they will send a request to our servers with the id of the link they clicked.
The server will then register that this link has been clicked, with data such as the ip of the person who clicked and the date.
After registering the action, the server will perform a redirection to the destination url.
This whole process is practically instant for the user who clicked the link.

### Who can I send tracked links to?

Make sure that the people you're going to send tracked links to are aware that their clicks will be registered.
Never send it without telling that you're collecting the person's activity, as it may constitute a privacy violation.


#### If you want to host the project on your own server, check the [deployment guide](DEPLOYMENT.md).
