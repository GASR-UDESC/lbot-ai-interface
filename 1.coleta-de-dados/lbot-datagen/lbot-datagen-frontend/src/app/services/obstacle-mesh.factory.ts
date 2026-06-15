import { Injectable } from '@angular/core';
import * as THREE from 'three';

export type ObstacleMeshType = 'crate' | 'wall' | 'ramp' | 'tree' | 'barrier' | 'stack' | 'industrial';

@Injectable({
  providedIn: 'root'
})
export class ObstacleMeshFactory {

  /**
   * Shade a hex color by a given percentage (-1.0 to 1.0)
   * Negative = darker, Positive = lighter
   */
  shadeColor(colorHex: string, percent: number): string {
    const num = parseInt(colorHex.replace('#', ''), 16);
    const amt = Math.round(255 * percent);
    const R = Math.min(255, Math.max(0, (num >> 16) + amt));
    const G = Math.min(255, Math.max(0, ((num >> 8) & 0x00FF) + amt));
    const B = Math.min(255, Math.max(0, (num & 0x0000FF) + amt));
    return '#' + (0x1000000 + R * 0x10000 + G * 0x100 + B).toString(16).slice(1);
  }

  private standardMaterial(colorHex: string): THREE.MeshStandardMaterial {
    return new THREE.MeshStandardMaterial({
      color: parseInt(colorHex.replace('#', ''), 16),
      roughness: 0.85,
      metalness: 0.1
    });
  }

  /**
   * Create a composite mesh for the given obstacle type
   */
  createMesh(
    type: ObstacleMeshType,
    width: number,
    height: number,
    depth: number,
    color: string,
    variation?: number,
    rampAngle?: number
  ): THREE.Group {
    switch (type) {
      case 'crate':
        return this.createCrateStack(width, height, depth, color, variation);
      case 'wall':
        return this.createWallWithPillars(width, height, depth, color, variation);
      case 'ramp':
        return this.createRamp(width, height, depth, color, variation, rampAngle);
      case 'tree':
        return this.createTree(width, height, depth, color, variation);
      case 'barrier':
        return this.createBarrier(width, height, depth, color, variation);
      case 'stack':
        return this.createStack(width, height, depth, color, variation);
      case 'industrial':
        return this.createIndustrial(width, height, depth, color, variation);
      default:
        return this.createFallbackBox(width, height, depth, color);
    }
  }

  /**
   * Crate stack: 2-3 boxes of varying sizes
   */
  createCrateStack(
    width: number,
    height: number,
    depth: number,
    color: string,
    variation?: number
  ): THREE.Group {
    const group = new THREE.Group();
    const count = variation !== undefined ? 2 + (Math.abs(variation) % 2) : 3;
    const baseMat = this.standardMaterial(color);
    const lightMat = this.standardMaterial(this.shadeColor(color, 0.15));
    const darkMat = this.standardMaterial(this.shadeColor(color, -0.15));

    for (let i = 0; i < count; i++) {
      const w = width * (0.6 + Math.random() * 0.4);
      const d = depth * (0.6 + Math.random() * 0.4);
      const h = height * (0.6 + Math.random() * 0.4);
      const geo = new THREE.BoxGeometry(w, h, d);
      const mat = i % 3 === 0 ? baseMat : (i % 3 === 1 ? lightMat : darkMat);
      const mesh = new THREE.Mesh(geo, mat);
      const prevY = i === 0
        ? 0
        : group.children[group.children.length - 1].position.y + ((group.children[group.children.length - 1] as THREE.Mesh).geometry as THREE.BoxGeometry)?.parameters?.height / 2;
      mesh.position.set(
        (Math.random() - 0.5) * (width - w) * 0.5,
        h / 2 + prevY,
        (Math.random() - 0.5) * (depth - d) * 0.5
      );
      mesh.castShadow = true;
      mesh.receiveShadow = true;
      group.add(mesh);
    }
    return group;
  }

  /**
   * Wall with pillars: main wall + 2 decorative pillars
   */
  createWallWithPillars(
    width: number,
    height: number,
    depth: number,
    color: string,
    variation?: number
  ): THREE.Group {
    const group = new THREE.Group();
    const mainMat = this.standardMaterial(color);
    const pillarMat = this.standardMaterial(this.shadeColor(color, -0.2));
    const capMat = this.standardMaterial(this.shadeColor(color, 0.2));

    // Main wall
    const wallGeo = new THREE.BoxGeometry(width * 0.9, height, depth * 0.9);
    const wall = new THREE.Mesh(wallGeo, mainMat);
    wall.position.y = height / 2;
    wall.castShadow = true;
    wall.receiveShadow = true;
    group.add(wall);

    // Left pillar
    const pSize = Math.min(width, depth) * 0.15;
    const pGeo = new THREE.BoxGeometry(pSize, height * 1.1, pSize);
    const pLeft = new THREE.Mesh(pGeo, pillarMat);
    pLeft.position.set(-width / 2 + pSize / 2, height * 1.1 / 2, 0);
    pLeft.castShadow = true;
    group.add(pLeft);

    // Right pillar
    const pRight = new THREE.Mesh(pGeo, pillarMat);
    pRight.position.set(width / 2 - pSize / 2, height * 1.1 / 2, 0);
    pRight.castShadow = true;
    group.add(pRight);

    // Caps
    const capGeo = new THREE.BoxGeometry(pSize * 1.3, pSize * 0.3, pSize * 1.3);
    const capLeft = new THREE.Mesh(capGeo, capMat);
    capLeft.position.set(-width / 2 + pSize / 2, height * 1.1 + pSize * 0.15, 0);
    group.add(capLeft);

    const capRight = new THREE.Mesh(capGeo, capMat);
    capRight.position.set(width / 2 - pSize / 2, height * 1.1 + pSize * 0.15, 0);
    group.add(capRight);

    return group;
  }

  /**
   * Ramp: inclined ramp + side rails
   */
  createRamp(
    width: number,
    height: number,
    depth: number,
    color: string,
    variation?: number,
    rampAngle?: number
  ): THREE.Group {
    const group = new THREE.Group();
    const rampMat = this.standardMaterial(color);
    const railMat = this.standardMaterial(this.shadeColor(color, -0.25));
    const angle = rampAngle ?? Math.PI / 8;

    // Main ramp
    const rampGeo = new THREE.BoxGeometry(width, height, depth);
    const ramp = new THREE.Mesh(rampGeo, rampMat);
    ramp.position.y = height / 2;
    ramp.rotation.x = angle;
    ramp.castShadow = true;
    ramp.receiveShadow = true;
    group.add(ramp);

    // Side rails
    const railHeight = height * 2;
    const railThick = Math.min(width, depth) * 0.1;
    const railGeo = new THREE.BoxGeometry(railThick, railHeight, depth);

    const railLeft = new THREE.Mesh(railGeo, railMat);
    railLeft.position.set(-width / 2 + railThick / 2, railHeight / 2, 0);
    railLeft.rotation.x = angle;
    railLeft.castShadow = true;
    group.add(railLeft);

    const railRight = new THREE.Mesh(railGeo, railMat);
    railRight.position.set(width / 2 - railThick / 2, railHeight / 2, 0);
    railRight.rotation.x = angle;
    railRight.castShadow = true;
    group.add(railRight);

    return group;
  }

  /**
   * Tree: trunk (cylinder) + canopy (sphere or cone)
   */
  createTree(
    width: number,
    height: number,
    depth: number,
    color: string,
    variation?: number
  ): THREE.Group {
    const group = new THREE.Group();
    const trunkColor = '#8B4513'; // brown trunk
    const trunkMat = this.standardMaterial(trunkColor);
    const canopyMat = this.standardMaterial(color);
    const canopyLightMat = this.standardMaterial(this.shadeColor(color, 0.2));

    const trunkRadius = Math.min(width, depth) * 0.2;
    const trunkHeight = height * 0.4;
    const trunkGeo = new THREE.CylinderGeometry(trunkRadius, trunkRadius * 1.2, trunkHeight, 8);
    const trunk = new THREE.Mesh(trunkGeo, trunkMat);
    trunk.position.y = trunkHeight / 2;
    trunk.castShadow = true;
    group.add(trunk);

    // Canopy: sphere or cone based on variation
    const canopyHeight = height * 0.6;
    const canopyRadius = Math.min(width, depth) * 0.5;
    if ((variation ?? 0) % 2 === 0) {
      const canopyGeo = new THREE.SphereGeometry(canopyRadius, 8, 6);
      const canopy = new THREE.Mesh(canopyGeo, canopyMat);
      canopy.position.y = trunkHeight + canopyRadius * 0.5;
      canopy.castShadow = true;
      group.add(canopy);
    } else {
      const canopyGeo = new THREE.ConeGeometry(canopyRadius, canopyHeight, 8);
      const canopy = new THREE.Mesh(canopyGeo, canopyMat);
      canopy.position.y = trunkHeight + canopyHeight / 2;
      canopy.castShadow = true;
      group.add(canopy);
    }

    // Secondary canopy detail
    const detailGeo = new THREE.SphereGeometry(canopyRadius * 0.5, 6, 4);
    const detail = new THREE.Mesh(detailGeo, canopyLightMat);
    detail.position.set(canopyRadius * 0.3, trunkHeight + canopyRadius * 0.3, canopyRadius * 0.2);
    detail.castShadow = true;
    group.add(detail);

    return group;
  }

  /**
   * Barrier: decorative cylinders + boxes
   */
  createBarrier(
    width: number,
    height: number,
    depth: number,
    color: string,
    variation?: number
  ): THREE.Group {
    const group = new THREE.Group();
    const baseMat = this.standardMaterial(color);
    const darkMat = this.standardMaterial(this.shadeColor(color, -0.2));
    const stripeMat = this.standardMaterial(this.shadeColor(color, 0.3));

    // Main horizontal bar
    const barGeo = new THREE.BoxGeometry(width, height * 0.3, depth * 0.4);
    const bar = new THREE.Mesh(barGeo, baseMat);
    bar.position.y = height * 0.7;
    bar.castShadow = true;
    group.add(bar);

    // Left post
    const postRadius = Math.min(width, depth) * 0.1;
    const postGeo = new THREE.CylinderGeometry(postRadius, postRadius, height, 8);
    const postLeft = new THREE.Mesh(postGeo, darkMat);
    postLeft.position.set(-width / 2 + postRadius, height / 2, 0);
    postLeft.castShadow = true;
    group.add(postLeft);

    // Right post
    const postRight = new THREE.Mesh(postGeo, darkMat);
    postRight.position.set(width / 2 - postRadius, height / 2, 0);
    postRight.castShadow = true;
    group.add(postRight);

    // Stripe on bar
    const stripeGeo = new THREE.BoxGeometry(width * 0.2, height * 0.32, depth * 0.42);
    const stripe = new THREE.Mesh(stripeGeo, stripeMat);
    stripe.position.y = height * 0.7;
    group.add(stripe);

    return group;
  }

  /**
   * Stack: industrial pile of boxes
   */
  createStack(
    width: number,
    height: number,
    depth: number,
    color: string,
    variation?: number
  ): THREE.Group {
    const group = new THREE.Group();
    const baseMat = this.standardMaterial(color);
    const darkMat = this.standardMaterial(this.shadeColor(color, -0.2));
    const lightMat = this.standardMaterial(this.shadeColor(color, 0.15));

    const layers = 2;
    const w = width * 0.5;
    const d = depth * 0.5;
    const h = height * 0.5;

    // Bottom layer: 2 boxes
    const b1 = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), baseMat);
    b1.position.set(-w / 2, h / 2, 0);
    b1.castShadow = true;
    group.add(b1);

    const b2 = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), darkMat);
    b2.position.set(w / 2, h / 2, 0);
    b2.castShadow = true;
    group.add(b2);

    // Top layer: 1 box
    const b3 = new THREE.Mesh(new THREE.BoxGeometry(w * 0.8, h, d * 0.8), lightMat);
    b3.position.set(0, h * 1.5, 0);
    b3.castShadow = true;
    group.add(b3);

    return group;
  }

  /**
   * Industrial: columns + beams + tanks
   */
  createIndustrial(
    width: number,
    height: number,
    depth: number,
    color: string,
    variation?: number
  ): THREE.Group {
    const group = new THREE.Group();
    const colMat = this.standardMaterial(color);
    const beamMat = this.standardMaterial(this.shadeColor(color, -0.15));
    const tankMat = this.standardMaterial(this.shadeColor(color, 0.2));

    const colRadius = Math.min(width, depth) * 0.12;
    const colHeight = height * 0.9;
    const colGeo = new THREE.CylinderGeometry(colRadius, colRadius, colHeight, 8);

    // Left column
    const colLeft = new THREE.Mesh(colGeo, colMat);
    colLeft.position.set(-width / 2 + colRadius * 2, colHeight / 2, 0);
    colLeft.castShadow = true;
    group.add(colLeft);

    // Right column
    const colRight = new THREE.Mesh(colGeo, colMat);
    colRight.position.set(width / 2 - colRadius * 2, colHeight / 2, 0);
    colRight.castShadow = true;
    group.add(colRight);

    // Beam connecting columns
    const beamGeo = new THREE.BoxGeometry(width * 0.6, height * 0.15, depth * 0.3);
    const beam = new THREE.Mesh(beamGeo, beamMat);
    beam.position.set(0, colHeight * 0.8, 0);
    beam.castShadow = true;
    group.add(beam);

    // Tank (sphere)
    const tankRadius = Math.min(width, depth) * 0.25;
    const tankGeo = new THREE.SphereGeometry(tankRadius, 8, 6);
    const tank = new THREE.Mesh(tankGeo, tankMat);
    tank.position.set(0, colHeight * 0.5, 0);
    tank.castShadow = true;
    group.add(tank);

    return group;
  }

  /**
   * Fallback simple box for unknown types
   */
  createFallbackBox(
    width: number,
    height: number,
    depth: number,
    color: string
  ): THREE.Group {
    const group = new THREE.Group();
    const geo = new THREE.BoxGeometry(width, height, depth);
    const mat = this.standardMaterial(color);
    const mesh = new THREE.Mesh(geo, mat);
    mesh.position.y = height / 2;
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    group.add(mesh);
    return group;
  }
}
