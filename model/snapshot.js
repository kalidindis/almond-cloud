// -*- mode: js; indent-tabs-mode: nil; js-basic-offset: 4 -*-
//
// This file is part of Thingpedia
//
// Copyright 2015 Giovanni Campagna <gcampagn@cs.stanford.edu>
//
// See COPYING for details

const db = require('../util/db');
const Q = require('q');

function create(client, snapshot) {
    var KEYS = ['description','date'];
    KEYS.forEach(function(key) {
        if (snapshot[key] === undefined)
            snapshot[key] = null;
    });
    snapshot['date'] = new Date;
    var vals = KEYS.map(function(key) {
        return snapshot[key];
    });
    var marks = KEYS.map(function() { return '?'; });

    return db.insertOne(client, 'insert into snapshot(' + KEYS.join(',') + ') values (' + marks.join(',') + ')', vals).then((id) => {
        snapshot.id = id;
        return db.query(client, 'insert into device_schema_snapshot select ?,device_schema.* from device_schema', [id]);
        return snapshot;
    });
}

module.exports = {
    create,

    getAll(client, start, end) {
        if (start !== undefined && end !== undefined) {
            return db.selectAll(client, "select * from snapshot order by snapshot_id asc limit ?,?",
                                [start, end]);
        } else {
            return db.selectAll(client, "select * from snapshot order by snapshot_id asc");
        }
    },
}