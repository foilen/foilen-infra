#!/usr/bin/python3

import os
import re

def isPlugin(project):
    return project.startswith('foilen-infra-plugin')
def isResource(project):
    return project.startswith('foilen-infra-resource')
def isSystem(project):
    return project.startswith('foilen-infra-system')

nodes = []
keptEdgeIds = []
everyEdgeIds = []
nextNodeId = 1
nodeIdByName = {}
nodeNameById = {}
def getProjectId(project):
    global nextNodeId
    global nodeIdByName
    global nodeNameById

    id = nodeIdByName.get(project)

    if not id:
        # create new id and node
        id = nextNodeId
        nextNodeId += 1
        nodeIdByName[project] = id
        nodeNameById[id] = project

        color = '#0FA'
        if isPlugin(project):
            color = '#0FF'
        if isResource(project):
            color = '#0AF'
        if isSystem(project):
            color = '#FAF'

        nodes.append("{id: " + str(id) + ", label:'" + project +"', color: '" + color + "'},")

    return id

def getSubProjects(project):
    includePattern = re.compile('include \'([^\']+)\'.*')
    projects = []
    if not os.path.exists(project + '/settings.gradle'):
        return ['']
    with open(project + '/settings.gradle') as settingsLines:
        for settingsLine in settingsLines:
            match = includePattern.match(settingsLine)
            if match and '_testing' not in match.group(1):
                projects.append(match.group(1))
    if not projects:
        return ['']
    return projects

# Go through all the projects
compilePattern = re.compile('.*compile.*com\.foilen:([^:]*):.*')
compileProjectPattern = re.compile('.*compile project\\(":([^"]*)"\\)')
with open('projects.txt') as projectsFile:
    for nextProject in projectsFile:
        nextProject = nextProject.strip()
        for toProject in getSubProjects(nextProject):
            # Empty name means no sub-projects
            buildFile = nextProject + '/' + toProject + '/build.gradle'
            if not toProject:
                toProject = nextProject

            toId = getProjectId(toProject)
            # Get all the dependencies
            with open(buildFile) as buildLines:
                for buildLine in buildLines:
                    match = compilePattern.match(buildLine)
                    if not match: match = compileProjectPattern.match(buildLine)
                    if match:
                        fromProject = match.group(1)
                        fromId = getProjectId(fromProject)
                        if toId:
                            keep = isResource(fromProject) and isResource(toProject)
                            keep |= not isResource(fromProject) and not isResource(toProject)
                            everyEdgeIds.append((fromId, toId))
                            if keep:
                                print(fromProject + " -> " + toProject)
                                keptEdgeIds.append((fromId, toId))

# Remove direct dependencies when there is a transitive one
allEdgeIds = keptEdgeIds.copy()
def canGetTo(fromId, startId):
    for edgeId in allEdgeIds:
        if edgeId[1] == fromId:
            if edgeId[0] == startId:
                return True
            else:
                if canGetTo(edgeId[0], startId):
                    return True
    return False

def hasTransitivePath(edgeId):
    start = edgeId[0]
    end = edgeId[1]
    for edgeId in allEdgeIds:
        if edgeId[1] == end and edgeId[0] != start:
            if canGetTo(edgeId[0], start):
                return True
    return False

changed = True
while changed:
    changed = False
    for edgeId in keptEdgeIds:
        if hasTransitivePath(edgeId):
            keptEdgeIds.remove(edgeId)
            changed = True

# Compute edges
edges = []
for edgeId in keptEdgeIds:
    edges.append("{from: " + str(edgeId[0]) + ", to: " + str(edgeId[1]) + ", arrows:'to'},")

# Save graph file
if not os.path.exists('docs'):
    os.makedirs('docs')

nodesText = "\n".join(nodes)
edgesText = "\n".join(edges)
with open('templates/dependencies.html') as template:
    with open('docs/projects-dependencies.html', 'w') as out:
        for line in template:
            line = line.replace('%NODES%', nodesText)
            line = line.replace('%EDGES%', edgesText)
            out.write(line)

# Save downstream files
def getDownstream(downstream, project):
    projectId = nodeIdByName[project]
    for edgeId in everyEdgeIds:
        if edgeId[0] == projectId:
            toId = edgeId[1]
            toName = nodeNameById[toId]
            if toName not in downstream:
                downstream.append(toName)
                getDownstream(downstream, toName)

for project, projectId in nodeIdByName.items():
    with open ('docs/downstream-' + project + '.txt', 'w') as out:
        downstream = []
        getDownstream(downstream, project)
        out.write("\n".join(downstream))
