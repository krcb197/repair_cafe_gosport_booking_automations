# Repair Cafe Gosport Booking Automations
This repository is a set of tools developed for making the 
administration of [Repair Cafe Gopsort](https://repaircafegosport.co.uk/) easier.

These tools are built around the [Tito](https://ti.to/) Event Platform. 

# Tools
There are three tools currently available described in the following sections

## Anonymous Event Booking Report
Generates an HTML report for the guests attending the next Repair Cafe Gosport event. 
This is intended to be emailed out to all the volunteers repairers so has the personal
details of the guests removed. 

The pictures provided by guests are uploaded to a Google Drive folder so that they can
be served up in the HTML report without needing to attach lots of pictures to an email

## Event Configuration Checker
Setting up an event in Tito by hand can be error prone, this runs a series of rule checks
To make sure the event is correctly configured, including:
- The event is set to the second saturday of the month, that matches is name
- The on and off sale times for tickets are setup correctly
- The start and end time of the activities are correct
